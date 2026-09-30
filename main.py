import os
import sys
import time
import tempfile
import argparse
from datetime import datetime
from typing import List

from config import (
    KEYWORDS_CONFIG,
    DEFAULT_AI_PROVIDER,
    SUPABASE_URL,
    SUPABASE_KEY
)
from database.local_store import LocalStore
from src.ai.analyzer import MultimodalAnalyzer
from src.media.stream_sampler import StreamSampler
from src.fetchers.youtube_live import YouTubeFetcher
from src.fetchers.tiktok_feed import TikTokFetcher
from src.fetchers.facebook_feed import FacebookFetcher
from src.fetchers.x_feed import TwitterFetcher
from src.fetchers.instagram_feed import InstagramFetcher
from src.exporters.gsheets import GoogleSheetsExporter
from src.exporters.obsidian import ObsidianExporter
from src.exporters.telegram import TelegramDispatcher

def process_single_item(
    feed_item,
    analyzer: MultimodalAnalyzer,
    local_store: LocalStore,
    obsidian_exp: ObsidianExporter,
    gsheets_exp: GoogleSheetsExporter,
    telegram_exp: TelegramDispatcher
):
    """ประมวลผลฟีด 1 รายการ: ดาวน์โหลดสตรีม/เสียง -> วิเคราะห์ AI -> บันทึกและแจ้งเตือน"""
    url = feed_item.url
    print(f"\n[{feed_item.platform}] กำลังประมวลผล: {url}")
    print(f"หัวข้อ/ข้อความ: {feed_item.title[:80]}...")

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path = None
        frame_paths = []

        # สกัดเสียงและภาพตัวอย่างจาก URL
        print("-> กำลังดึงแทร็กเสียงและภาพเฟรมตัวอย่างด้วย yt-dlp...")
        audio_path, frame_paths = StreamSampler.extract_audio_and_frames(
            media_url=url,
            output_dir=temp_dir,
            max_duration_seconds=120,
            extract_frames=True
        )

        combined_text = f"Title: {feed_item.title}\nCaption: {feed_item.caption}"
        if feed_item.is_live:
            combined_text += "\n[หมายเหตุ: รายการนี้กำลัง Live ถ่ายทอดสด]"

        print("-> กำลังประมวลผลและสกัดข้อมูลผู้ประสบภัย...")
        report = analyzer.analyze(
            text_content=combined_text,
            audio_path=audio_path,
            image_paths=frame_paths
        )

    # แปลงผลลัพธ์เป็น Dictionary สำหรับจัดเก็บ
    case_dict = report.model_dump()
    case_dict["source_url"] = url
    case_dict["platform"] = feed_item.platform
    case_dict["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    case_dict["case_status"] = "OPEN"

    # บันทึกสถานะว่าประมวลผลแล้ว
    local_store.mark_url_seen(url, feed_item.platform)

    if report.is_distress:
        print(f"🚨 ตรวจพบเคสขอความช่วยเหลือ! ระดับความด่วน: [{report.urgency_level}]")
        print(f"   ระดับน้ำ: {report.water_level} ({report.water_level_code})")
        print(f"   พิกัด: จ.{report.location.province} อ.{report.location.district} ต.{report.location.subdistrict}")
        print(f"   ต้องการ: {', '.join(report.needs)}")

        # 1. บันทึกลง Local SQLite
        local_store.save_case(case_dict)

        # 2. ส่งออกลง Obsidian Markdown
        card_file = obsidian_exp.export_case_card(case_dict)
        print(f"   บันทึกลง Obsidian Card: {card_file}")

        # 3. ส่งออกลง Google Sheets (ถ้าตั้งค่าไว้)
        if gsheets_exp.sheet:
            if gsheets_exp.append_case(case_dict):
                print("   บันทึกลง Google Sheets เรียบร้อยแล้ว")

        # 4. ส่งแจ้งเตือน Telegram (ถ้าตั้งค่าไว้)
        if telegram_exp.bot_token:
            if telegram_exp.send_alert(case_dict):
                print("   ส่งแจ้งเตือนเข้า Telegram เรียบร้อยแล้ว")
    else:
        print("ℹ️ โพสต์/คลิปนี้ไม่มีสัญญาณขอความช่วยเหลือฉุกเฉิน (ข่าวทั่วไปหรือสถานการณ์ปกติ)")

def run_scanner_loop(interval_minutes: int = 15):
    """รันสแกนตามช่วงเวลาแบบต่อเนื่อง"""
    analyzer = MultimodalAnalyzer()
    local_store = LocalStore()
    obsidian_exp = ObsidianExporter()
    gsheets_exp = GoogleSheetsExporter()
    telegram_exp = TelegramDispatcher()

    yt_fetcher = YouTubeFetcher()
    tiktok_fetcher = TikTokFetcher()
    fb_fetcher = FacebookFetcher()
    twitter_fetcher = TwitterFetcher()
    ig_fetcher = InstagramFetcher()

    keywords = KEYWORDS_CONFIG.get("search_keywords", ["น้ำท่วม"])
    provinces = KEYWORDS_CONFIG.get("monitored_provinces", ["ปราจีนบุรี", "เชียงราย"])

    print("=================================================================")
    print("🌊 เริ่มต้นระบบ FloodVoice Scanner (Automated Social Media Monitor)")
    print(f"AI Provider: {DEFAULT_AI_PROVIDER}")
    print(f"จังหวัดที่เฝ้าระวัง: {', '.join(provinces[:5])}...")
    print("=================================================================\n")

    while True:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] เริ่มรอบการตรวจจับฟีดใหม่...")

        # สุ่มรวมคำค้นกับจังหวัด
        search_queries = []
        for p in provinces[:3]: # หมุนเวียนตรวจสอบ
            search_queries.append([p, "น้ำท่วม"])

        for query_kws in search_queries:
            print(f">> กำลังค้นหาคีย์เวิร์ด: {' '.join(query_kws)}")
            
            # 1. ดึงจาก YouTube (รองรับ Live & Videos)
            yt_items = yt_fetcher.search_by_keywords(query_kws, max_results=3)
            for item in yt_items:
                if not local_store.is_url_seen(item.url):
                    process_single_item(item, analyzer, local_store, obsidian_exp, gsheets_exp, telegram_exp)

            # 2. ดึงจาก X / Twitter (ถ้ามี API Token)
            tw_items = twitter_fetcher.search_by_keywords(query_kws, max_results=3)
            for item in tw_items:
                if not local_store.is_url_seen(item.url):
                    process_single_item(item, analyzer, local_store, obsidian_exp, gsheets_exp, telegram_exp)

            # 3. ดึงจาก TikTok & Facebook & Instagram (ถ้ามี API Token)
            tt_items = tiktok_fetcher.search_by_keywords(query_kws, max_results=2)
            for item in tt_items:
                if not local_store.is_url_seen(item.url):
                    process_single_item(item, analyzer, local_store, obsidian_exp, gsheets_exp, telegram_exp)

            fb_items = fb_fetcher.search_by_keywords(query_kws, max_results=2)
            for item in fb_items:
                if not local_store.is_url_seen(item.url):
                    process_single_item(item, analyzer, local_store, obsidian_exp, gsheets_exp, telegram_exp)

            ig_items = ig_fetcher.search_by_keywords(query_kws, max_results=2)
            for item in ig_items:
                if not local_store.is_url_seen(item.url):
                    process_single_item(item, analyzer, local_store, obsidian_exp, gsheets_exp, telegram_exp)

        print(f"\nรอรอบถัดไปในอีก {interval_minutes} นาที...\n")
        time.sleep(interval_minutes * 60)

def main():
    parser = argparse.ArgumentParser(description="FloodVoice: Social Media Flood Distress Monitor")
    parser.add_argument("--scan", action="store_true", help="เริ่มวนลูปสแกน Social Media อัตโนมัติ")
    parser.add_argument("--interval", type=int, default=15, help="ระยะเวลาห่างแต่ละรอบ (นาที)")
    parser.add_argument("--test-url", type=str, help="ทดสอบประมวลผล URL วิดีโอ/Live โดยตรง 1 รายการ")
    parser.add_argument("--test-text", type=str, help="ทดสอบวิเคราะห์ข้อความโดยตรง")
    parser.add_argument("--list-cases", action="store_true", help="ดูรายการเคสที่บันทึกไว้ในฐานข้อมูล")

    args = parser.parse_args()

    analyzer = MultimodalAnalyzer()
    local_store = LocalStore()
    obsidian_exp = ObsidianExporter()
    gsheets_exp = GoogleSheetsExporter()
    telegram_exp = TelegramDispatcher()

    if args.test_text:
        print("กำลังทดสอบวิเคราะห์ข้อความ:")
        print(f"Input: {args.test_text}\n")
        report = analyzer.analyze(args.test_text)
        print("ผลลัพธ์การคัดกรองข้อมูล:")
        print(report.model_dump_json(indent=2))

    elif args.test_url:
        from src.fetchers.base import SocialFeedItem
        item = SocialFeedItem(
            platform="CustomURL",
            url=args.test_url,
            title="ทดสอบผ่านคำสั่ง CLI",
            caption="ทดสอบ URL โดยตรง"
        )
        process_single_item(item, analyzer, local_store, obsidian_exp, gsheets_exp, telegram_exp)

    elif args.list_cases:
        cases = local_store.get_all_cases()
        print(f"รายการเคสทั้งหมดที่บันทึกไว้ ({len(cases)} เคส):")
        for c in cases:
            print(f"- [{c['urgency_level']}] น้ำ: {c['water_level']} | จ.{c['province']} อ.{c['district']} | ต้องการ: {', '.join(c['needs'])}")

    elif args.scan:
        run_scanner_loop(interval_minutes=args.interval)

    else:
        # Default run: แสดง Help และสถานะ
        parser.print_help()
        print("\nตัวอย่างการใช้งาน:")
        print("  python main.py --scan                     # สั่งรันเฝ้าระวังอัตโนมัติ")
        print("  python main.py --test-text \"ช่วยด้วยครับ น้ำท่วมถึงอก ม.3 กบินทร์บุรี ติดอยู่ 4 คน ขอน้ำและเรือ\"")
        print("  python main.py --test-url https://www.youtube.com/watch?v=xxxx")

if __name__ == "__main__":
    main()
