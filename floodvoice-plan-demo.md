> From: https://gemini.google.com/app/bc12409054a9146a

# you asked

message time: 2026-09-30 16:01:20

ตอนนี้น้ำท่วมหลายพื้นที่หลายคนเดือดร้อน มีวิธีไหนบ้างที่จะไปอ่านวีดีโอ Facebook ,TikTok  ต่อ api ตัวไหนมอยสกจะอ่านวีดีโอ และถอดเป็นข้อความเพื่อจะเป็น data อยากจะรู้ว่าใครเดือดร่อน

---

# gemini response

การดึงข้อมูลวิดีโอจาก Facebook และ TikTok มาถอดเสียงเป็นข้อความเพื่อค้นหาผู้ประสบภัยน้ำท่วม สามารถแบ่ง Pipeline การทำงานออกเป็น 4 ขั้นตอนหลัก:

---

### 1. การดึงข้อมูลวิดีโอ (Video Sourcing & Collection)

ข้อจำกัดสำคัญคือทั้ง Facebook และ TikTok ไม่อนุญาตให้ Search วิดีโอสาธารณะทั่วไปแบบอิสระผ่าน API มาตรฐานสำหรับบุคคลธรรมดา

* **TikTok:**
  * **TikTok Research API (ทางการ):** รองรับการค้นหาวิดีโอตามคีย์เวิร์ด/แฮชแท็ก เช่น `#น้ำท่วม` แต่ต้องยื่นขอในนามนักวิจัยหรือสถาบันการศึกษา
  * **Scraper API / Service สำเร็จรูป (แนะนำสำหรับใช้งานด่วน):** เช่น **Apify** (TikTok Scraper Actors), **Bright Data**, หรือไลบรารี Python อย่าง `TikTokApi` (David Teather)
* **Facebook:**
  * **Meta Graph API (ทางการ):** ดึงได้เฉพาะเพจที่เราเป็นแอดมิน หรือกลุ่มที่ติดตั้งแอพของเราเท่านั้น ไม่อนุญาตให้ค้นหาโพสต์สาธารณะทั่วไป
  * **CrowdTangle:** ปิดตัวลงแล้ว
  * **แนวทางที่ใช้ได้จริง:** ใช้ Social Listening Tools (เช่น Zanroo, Mandala) หรือ Web Scraping Services ผ่าน **Apify (Facebook Post/Video Scraper)** เพื่อดึงโพสต์จากกลุ่มข่าว กลุ่มจิตอาสา หรือเพจรายงานภัยพิบัติประจำจังหวัด
* **การดาวน์โหลดไฟล์เสียงจาก URL:** เมื่อได้ URL วิดีโอมาแล้ว ใช้ไลบรารี Open-source เช่น `yt-dlp` เพื่อดึงเฉพาะแทร็กเสียง (`.mp3` หรือ `.wav`) ลงมาประมวลผลต่อ

---

### 2. การถอดเสียงเป็นข้อความภาษาไทย (Speech-to-Text)

เมื่อได้ไฟล์เสียง ให้ส่งเข้าโมเดลแปลงเสียงเป็นข้อความ (STT) ที่แม่นยำกับสำเนียงภาษาไทยและเสียงที่มีเสียงแทรก/เสียงน้ำ:

| เครื่องมือ / API | จุดเด่น | รูปแบบการคิดค่าบริการ |
| :--- | :--- | :--- |
| **OpenAI Whisper API (`whisper-1`)** | ถอดภาษาไทยได้ดีมาก ทนต่อเสียงรบกวน ใช้งานง่ายผ่าน REST API | จ่ายตามปริมาณการใช้งาน (~$0.006 / นาที) |
| **Faster-Whisper (Self-hosted)** | ใช้รันในเครื่องตัวเอง (ต้องมี GPU เช่น RTX 3060 ขึ้นไป) ฟรี ไม่มีโควตากวนใจ | ฟรี (Open-source) |
| **Google Cloud Speech-to-Text v2** | มีโมเดลภาษาไทย (`th-TH`) และรองรับการทำ Streaming Audio | มีโควตาฟรีต่อเดือน จากนั้นคิดตามนาที |
| **OpenThaiGPT / Thai National AI** | โมเดลภาษาไทยเฉพาะทาง | มีทั้งแบบ API และ Self-hosted |

---

### 3. การคัดกรองและสกัดข้อมูลผู้ประสบภัย (Information Extraction with LLM)

ข้อความที่ถอดได้มักยาวและมีทั้งข่าว ทัศนคติ หรือคำขอความช่วยเหลือจริง ให้ใช้ LLM (เช่น **Gemini 1.5 Flash**, **GPT-4o-mini**, หรือ **Claude 3.5 Haiku**) เข้ามาทำหน้าที่ประเมินความต้องการด้วย JSON Mode

**ตัวอย่าง System Prompt สำหรับสกัดข้อมูล:**

```text
จากข้อความที่ให้มา วิเคราะห์ว่าเป็น "คำขอความช่วยเหลือจากผู้ประสบภัยน้ำท่วม" หรือไม่ 
ถ้าใช่ ให้ตอบกลับเป็น JSON Format:
{
  "is_distress_call": true/false,
  "urgency_level": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",
  "location": "ระบุพิกัด/หมู่บ้าน/ตำบล/อำเภอ/จังหวัด ที่ต้องการความช่วยเหลือ",
  "contact": "เบอร์โทรศัพท์ หรือช่องทางติดต่อ",
  "needs": ["อาหาร", "เรือ", "อพยพผู้ป่วยติดเตียง", "ยารักษาโรค"],
  "headcount": "จำนวนคน/กลุ่มเสี่ยง",
  "summary": "สรุปสั้นๆ 1 ประโยค"
}
```

---

### 4. สถาปัตยกรรมระบบแบบสรุป (System Pipeline)

```text
[TikTok / FB Search (#น้ำท่วม)]
         │
         ▼
[Apify / Scraper / yt-dlp] ───► ดาวน์โหลดไฟล์ Audio (.m4a / .mp3)
         │
         ▼
[Whisper API / Faster-Whisper] ───► ถอดเสียงเป็น Text ภาษาไทย
         │
         ▼
[LLM (Gemini / GPT)] ───► ตรวจสอบความเดือดร้อน + สกัดพิกัด/เบอร์โทร
         │
         ▼
[Dashboard / Database / Google Sheets] ───► ส่งต่อทีมกู้ภัย/จิตอาสา
```

---

### ข้อควรระวังในการปฏิบัติงาน
1. **วิดีโอ Re-upload / ข้อความเก่า:** ในเหตุการณ์น้ำท่วมมักมีคลิปเก่าจากปีก่อนๆ ถูกนำมาโพสต์ใหม่ ควรตรวจจับ Metadata วันที่โพสต์ และใช้ LLM ช่วยตรวจสอบความสดใหม่ของข้อมูล
2. **เสียงเพลงแทรก (BGM):** คลิป TikTok มักใส่เพลงดังกลบเสียงพูด โมเดลจำพวก Whisper สามารถจัดการได้ระดับหนึ่ง แต่หากเสียงเพลงดังเกินไป อาจต้องใช้เครื่องมือแยกเสียงอย่าง `demucs` (Vocal Isolation) ก่อนส่งเข้า STT

<FollowUp label="ต้องการดูโค้ดตัวอย่าง Python สำหรับดาวน์โหลดเสียงและต่อเข้า Whisper API หรือไม่?" query="ขอโค้ดตัวอย่าง Python ที่ใช้ yt-dlp ดึงเสียงจากลิงก์วิดีโอแล้วส่งเข้า Whisper API เพื่อถอดข้อความภาษาไทย"/>

---

# you asked

message time: 2026-09-30 16:04:28

ได้ ขอตัวอย่างการดึง จาก api ,แต่ผมสนใจ เรื่องthirdparty ที่สามารถต่อ api Facebook ได้

---

# gemini response

การดึงข้อมูลโพสต์และวิดีโอจาก Facebook เพื่อเฝ้าระวังภัยพิบัติ การใช้ **Third-party Data Provider / Scraping API** เป็นทางเลือกที่ใช้งานได้จริงที่สุด เนื่องจาก Meta Graph API อย่างเป็นทางการไม่อนุญาตให้บุคคลทั่วไปค้นหา Public Posts/Videos แบบข้ามแพลตฟอร์มได้

---

### Third-party APIs ที่ดึงข้อมูล Facebook ได้จริง

| ผู้ให้บริการ | รูปแบบการทำงาน | เหมาะสำหรับ | ราคาเริ่มต้น |
| :--- | :--- | :--- | :--- |
| **Apify** | มี Actor สำเร็จรูป (เช่น *Facebook Posts Scraper*, *Facebook Video Scraper*) ต่อผ่าน REST API ได้ทันที | เริ่มต้นทำระบบเร็ว ค้นหาตามเพจข่าว/กลุ่มสาธารณะ | มี Free tier ($5 เครดิต/เดือน) |
| **Bright Data** | Web Scraper API มีเทมเพลต Facebook Pages, Reels, Posts และจัดการ Anti-bot/Proxy ให้เสร็จสรรพ | งาน Scale ใหญ่ ดึงข้อมูลหลักหมื่นถึงหลักแสนโพสต์ | Pay-as-you-go ตามปริมาณข้อมูล |
| **Phantombuster** | Cloud Automation ดึงคอมเมนต์ โพสต์กลุ่ม และเพจ Facebook | ดึงโพสต์และคอมเมนต์จากกลุ่มจิตอาสา/กลุ่มชุมชน | ทดลองฟรี 14 วัน จากนั้นเป็นรายเดือน |

> **กลยุทธ์การเฝ้าระวังน้ำท่วม:** ควรกำหนดเป้าหมายไปที่ URL ของ **เพจข่าวท้องถิ่น, สมาคมกู้ภัยประจำจังหวัด, และกลุ่มสาธารณะชุมชน** (เช่น "คนรักแม่ขรี", "กลุ่มข่าวพัทลุง", "แจ้งเหตุเชียงราย") เพื่อให้ API ดึงเฉพาะโพสต์ใหม่ ไม่จำเป็นต้องค้นหาแบบสุ่มทั้งระบบ

---

### ตัวอย่างโค้ด: ดึงวิดีโอจาก Facebook (ผ่าน Apify) -> ดึงเสียง -> ถอดข้อความ (Whisper API)

ติดตั้งไลบรารีที่จำเป็นก่อน:
```bash
pip install apify-client yt-dlp openai
```

```python
import os
import tempfile
import yt_dlp
from apify_client import ApifyClient
from openai import OpenAI

# 1. ตั้งค่า API Keys
APIFY_TOKEN = "YOUR_APIFY_TOKEN"
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"

apify_client = ApifyClient(APIFY_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def get_facebook_recent_posts(target_page_url: str, max_posts: int = 5):
    """ดึงโพสต์ล่าสุดจาก Facebook Page ผ่าน Apify Actor"""
    run_input = {
        "startUrls": [{"url": target_page_url}],
        "resultsLimit": max_posts,
    }
    # ใช้ Actor facebook-posts-scraper มาตรฐานของ Apify
    run = apify_client.actor("apify/facebook-posts-scraper").call(run_input=run_input)
    
    posts = []
    for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
        posts.append({
            "post_id": item.get("id"),
            "url": item.get("url") or item.get("postUrl"),
            "caption": item.get("text", ""),
            "video_url": item.get("media", [{}])[0].get("url") if item.get("media") else None
        })
    return posts


def extract_audio_from_url(video_url: str, output_path: str):
    """ดาวน์โหลดเฉพาะแทร็กเสียงจาก URL วิดีโอด้วย yt-dlp"""
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
        "quiet": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


def transcribe_audio_to_text(audio_file_path: str) -> str:
    """ส่งไฟล์เสียงเข้า OpenAI Whisper เพื่อถอดเป็นภาษาไทย"""
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="th"  # ระบุภาษาไทยเพื่อความแม่นยำ
        )
    return transcript.text


def analyze_flood_distress(text: str) -> str:
    """ใช้ LLM วิเคราะห์หาพิกัดและความต้องการช่วยเหลือ"""
    prompt = f"""
    วิเคราะห์ข้อความต่อไปนี้ว่ามีผู้ประสบภัยน้ำท่วมขอความช่วยเหลือหรือไม่:
    "{text}"
    
    ตอบเป็น JSON format เท่านั้น:
    {{
      "is_distress": true/false,
      "location": "ตำบล/อำเภอ/พิกัด หรือระบุ 'ไม่ระบุ'",
      "contact": "เบอร์ติดต่อ หรือระบุ 'ไม่ระบุ'",
      "urgency": "HIGH / MEDIUM / LOW",
      "needs": ["ระบุสิ่งที่ต้องการ เช่น ข้าวสาร น้ำดื่ม เรืออพยพ"]
    }}
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content


# --- ตัวอย่างการรัน Pipeline ---
if __name__ == "__main__":
    # ตัวอย่าง: ดึงข้อมูลจากเพจกู้ภัยหรือเพจข่าวท้องถิ่น
    target_page = "https://www.facebook.com/example.rescue.page"
    
    print("1. กำลังดึงโพสต์จาก Facebook...")
    posts = get_facebook_recent_posts(target_page, max_posts=3)

    for idx, post in enumerate(posts, 1):
        print(f"\n--- กำลังตรวจโพสต์ที่ {idx}: {post['url']} ---")
        
        # กรณีที่โพสต์มีข้อความ caption ชัดเจนอยู่แล้ว ให้ตรวจก่อน
        if post["caption"]:
            print(f"ข้อความประกอบ: {post['caption'][:80]}...")

        # หากมีลิงก์วิดีโอ ให้นำมาถอดเสียง
        video_url = post["video_url"] or post["url"]
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_base_path = os.path.join(temp_dir, f"audio_{idx}")
            expected_mp3 = f"{audio_base_path}.mp3"
            
            try:
                print("2. กำลังดึงเสียงจากวิดีโอ...")
                extract_audio_from_url(video_url, audio_base_path)
                
                if os.path.exists(expected_mp3):
                    print("3. กำลังถอดเสียงด้วย Whisper...")
                    transcribed_text = transcribe_audio_to_text(expected_mp3)
                    print(f"ข้อความที่ถอดได้: {transcribed_text[:120]}...")
                    
                    print("4. วิเคราะห์ด้วย LLM...")
                    combined_text = f"Caption: {post['caption']}\nAudio: {transcribed_text}"
                    result = analyze_flood_distress(combined_text)
                    print(f"ผลลัพธ์: {result}")
            except Exception as e:
                print(f"ข้ามวิดีโอนี้เนื่องจากไม่สามารถดึงเสียงได้: {e}")
```

<FollowUp label="ต้องการให้เขียนฟังก์ชันส่งแจ้งเตือนเข้า LINE Notify/Telegram อัตโนมัติเมื่อพบเคสฉุกเฉินหรือไม่?" query="ขอโค้ดตัวอย่าง Python ส่งแจ้งเตือนข้อมูลผู้ประสบภัยที่สกัดได้เข้า Telegram Bot หรือ LINE Notify อัตโนมัติ"/>

---

# you asked

message time: 2026-09-30 16:08:27

ได้

---

# gemini response

การส่งข้อความแจ้งเตือนเมื่อระบบตรวจพบเคสเดือดร้อน ขอแนะนำ **Telegram Bot** เพราะทำง่าย ฟรี ไม่มีข้อจำกัดเรื่องโควตา และสร้างห้องแชต/กลุ่มสำหรับทีมกู้ภัยเข้ามารับเคสได้ทันที 

*(หมายเหตุ: บริการ LINE Notify แบบดั้งเดิมยุติการให้บริการแล้ว หากใช้ฝั่ง LINE จำเป็นต้องสร้าง **LINE Official Account (LINE Messaging API)** ซึ่งมีขั้นตอนลงทะเบียน webhook เพิ่มเติม)*

---

### ขั้นตอนเตรียม Telegram Bot (ใช้เวลา 2 นาที)
1. ทักหา `@BotFather` ใน Telegram กด `/newbot` แล้วตั้งชื่อบอท จะได้ `TELEGRAM_BOT_TOKEN`
2. สร้างกลุ่ม Telegram ดึงบอทเข้ากลุ่ม แล้วส่งข้อความอะไรก็ได้ 1 ข้อความ
3. เข้า URL: `[https://api.telegram.org/bot](https://api.telegram.org/bot)<YOUR_BOT_TOKEN>/getUpdates` มองหา `"chat":{"id": -xxxxxxxxx}` นั่นคือ `TELEGRAM_CHAT_ID`

---

### โค้ดฟังก์ชันส่งแจ้งเตือนและผสานเข้ากับ Pipeline

ติดตั้งไลบรารีส่ง HTTP Request (หากยังไม่มี):
```bash
pip install requests
```

```python
import json
import requests

TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_OR_GROUP_ID"


def send_telegram_alert(case_data: dict, source_url: str):
    """ส่งข้อความสรุปเคสฉุกเฉินเข้าห้อง Telegram"""
    urgency_emoji = {
        "HIGH": "🔴 ด่วนที่สุด",
        "MEDIUM": "🟡 ปานกลาง",
        "LOW": "🟢 ทั่วไป"
    }

    urgency_label = urgency_emoji.get(case_data.get("urgency", "MEDIUM"), "⚠️ แจ้งเหตุ")
    needs_str = ", ".join(case_data.get("needs", [])) or "ไม่ได้ระบุ"

    # จัดรูปแบบข้อความแจ้งเตือนสำหรับทีมกู้ภัย/จิตอาสา
    message = (
        f"{urgency_label} - พบผู้ประสบภัยน้ำท่วม\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 พิกัด/พื้นที่: {case_data.get('location', 'ไม่ระบุ')}\n"
        f"📞 เบอร์ติดต่อ: {case_data.get('contact', 'ไม่ระบุ')}\n"
        f"📦 สิ่งที่ต้องการ: {needs_str}\n"
        f"🔗 ที่มา: {source_url}\n"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print(">> ส่งแจ้งเตือน Telegram สำเร็จ")
    except Exception as e:
        print(f">> ส่งแจ้งเตือน Telegram ล้มเหลว: {e}")
```

---

### วิธีนำไปต่อท้ายขั้นตอนวิเคราะห์ของเดิม

ในลูปที่รัน LLM จากโค้ดเดิม ให้แปลงผลลัพธ์ JSON แล้วส่งต่อเข้าฟังก์ชันแจ้งเตือนทันที:

```python
# แปลงผลลัพธ์จาก LLM ที่เป็น JSON String เป็น Dict
analysis_result = json.loads(result)

# ตรวจสอบว่าเข้าข่ายเคสขอความช่วยเหลือหรือไม่
if analysis_result.get("is_distress") is True:
    print(f"ตรวจพบเคสเดือดร้อนระดับ: {analysis_result.get('urgency')}")
    
    # ส่งแจ้งเตือนเข้ากลุ่มกู้ภัย
    send_telegram_alert(
        case_data=analysis_result,
        source_url=post["url"]
    )
else:
    print("โพสต์นี้เป็นข่าวทั่วไป/ไม่มีการขอความช่วยเหลือ ข้ามการแจ้งเตือน")
```

<FollowUp label="ต้องการดูวิธีบันทึกข้อมูลลง Google Sheets อัตโนมัติเป็น Database กลางด้วยไหม?" query="ขอโค้ดตัวอย่าง Python บันทึกข้อมูลพิกัดและเคสผู้ประสบภัยลง Google Sheets อัตโนมัติด้วย gspread"/>

---

# you asked

message time: 2026-09-30 16:09:07

ทำไมต้องทักหา @BotFatther

---

# gemini response

**`@BotFather`** เป็นบัญชีบอททางการของ Telegram ที่ทำหน้าที่เป็น **"ระบบจัดการและสร้างบอททั้งหมดบน Telegram"** (เปรียบเหมือนแอดมินระบบของแพลตฟอร์ม)

สาเหตุที่ต้องทักหา `@BotFather` มีเหตุผลหลัก 3 ข้อ:

1. **ขอ API Token สำหรับเขียนโปรแกรม:** Telegram ไม่อนุญาตให้โค้ดสั่งส่งข้อความเข้าห้องแชตได้โดยตรงหากไม่มีตัวตน การทัก `@BotFather` แล้วสั่ง `/newbot` คือวิธีเดียวในการออก **API Token** (กุญแจยืนยันสิทธิ์) เพื่อให้โค้ด Python เชื่อมต่อและสั่งให้บอทพิมพ์ข้อความได้
2. **สร้างตัวตนบอท (Bot Account):** เพื่อกำหนดชื่อบอท (Display Name) และ Username (เช่น `@FloodRescueAlertBot`) เพื่อให้เราสามารถค้นหาและดึงตัวบอทนี้เข้ากลุ่มกู้ภัย/จิตอาสาได้
3. **ตั้งค่าสิทธิ์และความปลอดภัย:** ใช้เปิด-ปิดการอนุญาตให้บอทเข้ากลุ่ม (`/setjoingroups`) หรือตั้งค่าคำอธิบายการทำงานของบอท

สรุปคือ Telegram ออกแบบให้ไม่ต้องเข้าหน้าเว็บ Developer Portal เหมือน Facebook หรือ Google แค่คุยกับ `@BotFather` ผ่านแอปแชตโดยตรง ก็จะได้ API Key มาใช้งานได้ทันที

---

# you asked

message time: 2026-09-30 16:09:43

หรอ มันไม่ไสามารถ สร้างเองได้หรอ ต้องทักเท่านั้นหรอ

---

# gemini response

**ใช่ครับ ต้องทักคุยกับ `@BotFather` เท่านั้น** เป็นวิธีเดียวของ Telegram เลย 

เหตุผลคือ:

1. **Telegram ไม่มีเว็บหน้า Dashboard สำหรับสร้างบอท:** แพลตฟอร์มอื่นอย่าง Facebook, Google หรือ LINE จะมีเว็บ Developer Console (กดยื่นฟอร์ม ยืนยันอีเมล สมัครบัตรเครดิต ฯลฯ) แต่ Telegram ไม่มีหน้าเว็บแบบนั้นสำหรับสร้างบอท
2. **เขาออกแบบระบบให้เป็น "Chat-First":** ทาง Telegram ใช้ไอเดียว่า *“ในเมื่อเราเป็นแอปแชต การสร้างและจัดการบอทก็ควรทำผ่านการแชตให้จบไปเลย”* จึงสร้างบัญชีระบบชื่อ **`@BotFather`** ขึ้นมาทำหน้าที่เป็น Admin กลาง คอยรับคำสั่งผ่านแชต ออก Token และจัดการบอททั้งหมดในระบบ

---

### วิธีทักแบบสั้นที่สุด (ไม่ถึง 1 นาทีเสร็จ)

1. ค้นหาในช่อง Search ของ Telegram พิมพ์: `@BotFather` *(สังเกตเครื่องหมายติ๊กถูกสีฟ้าข้างชื่อ)*
2. กดปุ่ม **Start** แล้วพิมพ์ส่งไปว่า:
   ```text
   /newbot
   ```
3. บอทจะถาม 2 อย่าง:
   * **ชื่อบอท (Display Name):** พิมพ์อะไรก็ได้ เช่น `Flood Rescue Alert`
   * **Username บอท:** ต้องลงท้ายด้วยคำว่า `bot` เช่น `flood_rescue_alert_bot`
4. เสร็จแล้ว `@BotFather` จะตอบกลับมาเป็นข้อความยาวๆ ที่มี **API Token** (รหัสยาวๆ เช่น `7123456789:AAH...`) ก๊อบปี้ค่านั้นไปวางในโค้ด Python ได้ทันทีครับ

---

# you asked

message time: 2026-09-30 16:10:49

ทักยังไงช่องทางไหน

---

# gemini response

ทักผ่าน**แอป Telegram** โดยตรงเลยครับ ทำได้ทั้งบนมือถือ (iOS / Android) หรือบนคอมพิวเตอร์ (เว็บ/โปรแกรม)

---

### วิธีที่ 1: กดผ่านลิงก์โดยตรง (เร็วที่สุด)
คลิกลิงก์นี้ได้เลย: **[https://t.me/BotFather](https://t.me/BotFather)** 
* ระบบจะเปิดห้องแชตกับ `@BotFather` ในแอป Telegram ให้ทันที

---

### วิธีที่ 2: ค้นหาในแอป Telegram

1. เปิดแอป **Telegram**
2. ไปที่ **ช่องค้นหา (Search)** ด้านบนสุด
3. พิมพ์ค้นหาว่า:
   ```text
   @BotFather
   ```
4. เลือกผลลัพธ์แรกที่เป็นรูปตัวการ์ตูนใส่แว่นดำ และมี **เครื่องหมายติ๊กถูกสีฟ้า (Verified badge)** ด้านหลังชื่อ
5. กดปุ่ม **Start** ด้านล่างห้องแชตเพื่อเริ่มใช้งาน แล้วพิมพ์ `/newbot` ได้เลยครับ

---

# you asked

message time: 2026-09-30 16:13:17

เป็นไปได้ไหม เราจะสร้าง template หรือชุด code ลง GitHub เพื่อที่จะช่วยเหลือ น้ำท่วม

---

# gemini response

เป็นไปได้อย่างยิ่ง และเป็นไอเดียที่ดีมากสำหรับโครงการอาสาสมัครแบบ Open-source ชุมชนนักพัฒนาหรือทีมกู้ภัยสามารถ Clone โปรเจกต์ไปรันบน Server หรือเครื่องตัวเองได้ทันที

โครงสร้างโปรเจกต์ Template ที่นำไปขึ้น GitHub ควรจัดเป็นระเบียบ แบ่งโมดูลชัดเจน และรองรับ Docker เพื่อให้รันได้ในคำสั่งเดียว

---

### 1. โครงสร้างไฟล์ใน Repository (Project Structure)

```text
flood-distress-detector/
├── .env.example              # ตัวอย่างไฟล์ตั้งค่า API Keys
├── .gitignore
├── README.md                 # คู่มือการติดตั้งและใช้งานภาษาไทย/อังกฤษ
├── requirements.txt          # ไลบรารี Python
├── Dockerfile                # สำหรับรันแบบ Container
├── docker-compose.yml
├── config.py                 # โหลด Environment Variables
├── main.py                   # ตัวรัน Pipeline หลัก
└── src/
    ├── __init__.py
    ├── fetcher.py            # ดึงข้อมูลจาก Apify / Social Media
    ├── audio.py              # สกัดไฟล์เสียงด้วย yt-dlp
    ├── transcriber.py        # ถอดเสียงด้วย Whisper
    ├── extractor.py          # คัดกรองและสกัดข้อมูลด้วย LLM
    └── notifier.py           # ส่งแจ้งเตือน Telegram / Google Sheets
```

---

### 2. โค้ดแม่แบบแยกแต่ละโมดูล

#### `requirements.txt`
```text
apify-client>=1.6.0
yt-dlp>=2024.8.6
openai>=1.30.0
requests>=2.31.0
pydantic>=2.0.0
python-dotenv>=1.0.0
```

#### `.env.example`
```env
APIFY_TOKEN=your_apify_api_token
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
TARGET_FACEBOOK_URLS=https://www.facebook.com/rescue_page_1,https://www.facebook.com/rescue_page_2
CHECK_INTERVAL_MINUTES=15
```

#### `src/extractor.py` (ใช้ Pydantic เพื่อบีบ Structured JSON ให้แม่นยำ)
```python
from pydantic import BaseModel, Field
from openai import OpenAI
import os

class DistressReport(BaseModel):
    is_distress: bool = Field(description="เป็นโพสต์ขอความช่วยเหลือเหตุน้ำท่วมจริงหรือไม่")
    urgency: str = Field(description="ระดับความด่วน: CRITICAL, HIGH, MEDIUM, LOW")
    location: str = Field(description="พิกัด หมู่บ้าน ตำบล อำเภอ หรือจุดสังเกต")
    contact: str = Field(description="เบอร์โทรศัพท์ หรือชื่อผู้ติดต่อ")
    needs: list[str] = Field(description="สิ่งที่ต้องการ เช่น ข้าวสาร น้ำดื่ม เรือ อพยพคนแก่")
    summary: str = Field(description="สรุปเหตุการณ์ 1 ประโยค")

def analyze_text(text: str, client: OpenAI) -> DistressReport:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "คุณคือ AI กู้ภัย มีหน้าที่คัดกรองเคสขอความช่วยเหลือเหตุน้ำท่วมจากข้อความ"},
            {"role": "user", "content": text},
        ],
        response_format=DistressReport,
    )
    return completion.choices[0].message.parsed
```

#### `src/notifier.py`
```python
import requests

def send_alert(report, source_url: str, bot_token: str, chat_id: str):
    if not report.is_distress:
        return

    urgency_tag = {
        "CRITICAL": "🚨 วิกฤตด่วนที่สุด",
        "HIGH": "🔴 ด่วนมาก",
        "MEDIUM": "🟡 ปานกลาง",
        "LOW": "🟢 ทั่วไป"
    }.get(report.urgency, "⚠️ แจ้งเหตุ")

    needs_text = ", ".join(report.needs) if report.needs else "ไม่ระบุ"
    message = (
        f"{urgency_tag} (ตรวจพบเคสน้ำท่วม)\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 พื้นที่: {report.location}\n"
        f"📞 ติดต่อ: {report.contact}\n"
        f"📦 ต้องการ: {needs_text}\n"
        f"📝 สรุป: {report.summary}\n"
        f"🔗 ลิงก์ต้นทาง: {source_url}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)
```

---

### 3. ตัวอย่างเนื้อหา `README.md` สำหรับ GitHub

```markdown
# 🌊 Flood Distress Detector (AI บอทคัดกรองผู้ประสบภัยน้ำท่วม)

เครื่องมือ Open-source ช่วยดึงวิดีโอ/โพสต์จาก Social Media ถอดเสียงภาษาไทยด้วย AI (Whisper) 
และคัดกรองข้อมูลเคสขอความช่วยเหลือ (พิกัด, สิ่งที่ต้องการ, เบอร์ติดต่อ) ส่งแจ้งเตือนกู้ภัยผ่าน Telegram แบบอัตโนมัติ

## 🚀 วิธีติดตั้งและใช้งาน

1. โคลน Repository:
   git clone https://github.com/your-username/flood-distress-detector.git
   cd flood-distress-detector

2. ตั้งค่า Environment:
   cp .env.example .env
   # กรอก API Keys ของ Apify, OpenAI และ Telegram ในไฟล์ .env

3. ติดตั้ง Dependencies และรัน:
   pip install -r requirements.txt
   python main.py

## 🤝 ร่วมพัฒนา (Contributing)
- เพิ่มตัวรองรับ Platform อื่น (TikTok, X/Twitter)
- ปรับแต่ง Prompt ภาษาถิ่น (เช่น ภาษาใต้, ภาษาอีสาน, คำเมือง)
```

---

### จุดเด่นที่จะดึงดูดให้อาสาสมัครคนอื่นมาร่วมต่อยอด
1. **โมดูลล่าร์ (Modular):** ใครอยากเปลี่ยนไปใช้ **Faster-Whisper** บนเครื่องตัวเอง (ไม่ต้องเสียเงินค่า API) ก็แค่แก้ไฟล์ `transcriber.py`
2. **จัดการเรื่องคำค้นท้องถิ่น:** ภาษาพูดในวิดีโอน้ำท่วมมักมีภาษาถิ่น การเปิด Repo ให้นักพัฒนาในแต่ละพื้นที่ช่วยกันปรับแต่ง Prompt หรือคำสั่ง Whisper จะช่วยเพิ่มความแม่นยำได้สูงขึ้น

<FollowUp label="ต้องการให้เขียนโค้ดเต็มไฟล์ main.py และ Dockerfile พร้อมรันเลยไหม?" query="ขอโค้ดไฟล์ main.py แบบสมบูรณ์และ Dockerfile สำหรับโปรเจกต์ flood-distress-detector"/>

---

# you asked

message time: 2026-09-30 16:14:24

ได้

---

# gemini response

นี่คือชุดโค้ดไฟล์ที่เหลือสำหรับสร้าง Repository บน GitHub ให้สามารถรันและนำไป Deploy ด้วย Docker ได้ทันที:

---

### 1. `main.py` (ไฟล์ควบคุมกระบวนการทั้งหมด)

ทำหน้าที่วนลูปทำงานตามช่วงเวลาที่กำหนด จัดการไฟล์ชั่วคราว และป้องกันการประมวลผลโพสต์ซ้ำ

```python
import os
import time
import tempfile
from dotenv import load_dotenv
from openai import OpenAI
from apify_client import ApifyClient

from src.fetcher import fetch_target_posts
from src.audio import extract_audio
from src.transcriber import transcribe_audio
from src.extractor import analyze_text
from src.notifier import send_alert

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TARGET_URLS = [u.strip() for u in os.getenv("TARGET_FACEBOOK_URLS", "").split(",") if u.strip()]
INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))

apify_client = ApifyClient(APIFY_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# เก็บ ID โพสต์ที่เคยประมวลผลแล้วเพื่อไม่ให้ตรวจซ้ำ
processed_post_ids = set()

def run_pipeline():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] กำลังเริ่มรอบการตรวจจับ...")
    
    for page_url in TARGET_URLS:
        print(f">> ตรวจสอบเพจ: {page_url}")
        posts = fetch_target_posts(apify_client, page_url, max_posts=5)
        
        for post in posts:
            post_id = post["post_id"]
            if post_id in processed_post_ids:
                continue
            
            processed_post_ids.add(post_id)
            print(f"-> ตรวจพบโพสต์ใหม่: {post['url']}")
            
            combined_context = f"Caption: {post['caption']}"
            
            # หากมีวิดีโอ ดึงเสียงและถอดข้อความ
            if post["video_url"]:
                with tempfile.TemporaryDirectory() as temp_dir:
                    audio_path = os.path.join(temp_dir, "temp_audio")
                    expected_mp3 = f"{audio_path}.mp3"
                    
                    if extract_audio(post["video_url"], audio_path):
                        transcription = transcribe_audio(expected_mp3, openai_client)
                        if transcription:
                            combined_context += f"\nVideo Audio: {transcription}"

            # สกัดข้อมูลด้วย LLM
            report = analyze_text(combined_context, openai_client)
            
            # แจ้งเตือนเมื่อเป็นเคสฉุกเฉิน
            if report.is_distress:
                print(f"🚨 พบเคสขอความช่วยเหลือ! ระดับ: {report.urgency}")
                send_alert(report, post["url"], TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
            else:
                print("ℹ️ ไม่ใช่การขอความช่วยเหลือฉุกเฉิน")

def main():
    if not all([APIFY_TOKEN, OPENAI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
        raise ValueError("กรุณากรอก Environment Variables ในไฟล์ .env ให้ครบถ้วน")
        
    print("เริ่มการทำงานของระบบ Flood Distress Detector...")
    while True:
        try:
            run_pipeline()
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการทำงาน: {e}")
            
        print(f"รอรอบถัดไปในอีก {INTERVAL_MINUTES} นาที...\n")
        time.sleep(INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main()
```

---

### 2. โมดูลย่อยในโฟลเดอร์ `src/`

#### `src/fetcher.py`
```python
from apify_client import ApifyClient

def fetch_target_posts(client: ApifyClient, page_url: str, max_posts: int = 5) -> list[dict]:
    run_input = {
        "startUrls": [{"url": page_url}],
        "resultsLimit": max_posts,
    }
    try:
        run = client.actor("apify/facebook-posts-scraper").call(run_input=run_input)
        posts = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            posts.append({
                "post_id": item.get("id") or item.get("url"),
                "url": item.get("url") or item.get("postUrl"),
                "caption": item.get("text", ""),
                "video_url": item.get("media", [{}])[0].get("url") if item.get("media") else None
            })
        return posts
    except Exception as e:
        print(f"ดึงข้อมูล Facebook ไม่สำเร็จ: {e}")
        return []
```

#### `src/audio.py`
```python
import yt_dlp

def extract_audio(video_url: str, output_path: str) -> bool:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return True
    except Exception as e:
        print(f"ไม่สามารถดาวน์โหลดเสียงจากวิดีโอได้: {e}")
        return False
```

#### `src/transcriber.py`
```python
import os
from openai import OpenAI

def transcribe_audio(audio_file_path: str, client: OpenAI) -> str:
    if not os.path.exists(audio_file_path):
        return ""
    try:
        with open(audio_file_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="th"
            )
        return transcript.text
    except Exception as e:
        print(f"ถอดเสียงไม่สำเร็จ: {e}")
        return ""
```

---

### 3. `Dockerfile`

ใช้ Base Image Python พร้อมติดตั้ง `ffmpeg` ซึ่งจำเป็นสำหรับการสกัดไฟล์เสียงของ `yt-dlp`

```dockerfile
FROM python:3.11-slim

# ติดตั้ง ffmpeg สำหรับแปลงไฟล์เสียง
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ก็อปปี้ dependencies และติดตั้ง
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ก็อปปี้ซอร์สโค้ดเข้า container
COPY . .

# กำหนดให้รันแบบ unbuffered เพื่อให้ log แสดงทันที
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
```

---

### 4. `docker-compose.yml`

ช่วยให้ผู้ใช้ที่โคลน Repository ไป สามารถสั่งรันด้วยคำสั่งเดียว:

```yaml
version: '3.8'

services:
  flood-detector:
    build: .
    container_name: flood_distress_detector
    restart: unless-stopped
    env_file:
      - .env
```

---

### คำสั่งสำหรับขึ้น GitHub ครั้งแรก

```bash
git init
git add .
git commit -m "feat: initial flood distress detector template"
git branch -M main
git remote add origin https://github.com/<your-username>/flood-distress-detector.git
git push -u origin main
```

ผู้ใช้คนอื่นสามารถใช้งานได้ทันทีเพียงรัน:
```bash
cp .env.example .env
# แก้ไขค่าคีย์ต่างๆ ใน .env
docker compose up -d --build
```

<FollowUp label="ต้องการให้เขียน GitHub Actions Workflow สำหรับตรวจสอบความถูกต้องของโค้ด (CI/CD) ด้วยไหม?" query="ขอไฟล์ GitHub Actions CI workflow สำหรับทดสอบ linting และ syntax ของโปรเจกต์นี้"/>

---

# you asked

message time: 2026-09-30 16:15:07

อยากจะให้สร้าง zip file ให้ผม upload เองได้ไหม

---

# gemini response

เนื่องจากในระบบแชตนี้ไม่สามารถสร้างหรือส่งไฟล์ `.zip` ให้ดาวน์โหลดตรงๆ ได้ แต่คุณสามารถสร้างไฟล์ zip ทั้งหมดนี้ได้เองในเครื่องทันทีด้วย **Python Script เพียงไฟล์เดียว**

เพียงสร้างไฟล์ชื่อ `build_repo.py` ในเครื่องของคุณ นำโค้ดด้านล่างนี้ไปวาง แล้วรันคำสั่ง:

```bash
python build_repo.py
```

สคริปต์จะสร้างโฟลเดอร์ไฟล์โค้ดทั้งหมด พร้อมบีบอัดออกมาเป็นไฟล์ **`flood-distress-detector.zip`** ให้ทันที นำไปอัปโหลดขึ้น GitHub ได้เลย

---

### โค้ด `build_repo.py`

```python
import os
import zipfile

# 1. นิยามโครงสร้างไฟล์และเนื้อหาทั้งหมดของโปรเจกต์
PROJECT_FILES = {
    "requirements.txt": """apify-client>=1.6.0
yt-dlp>=2024.8.6
openai>=1.30.0
requests>=2.31.0
pydantic>=2.0.0
python-dotenv>=1.0.0
""",

    ".env.example": """APIFY_TOKEN=your_apify_api_token
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
TARGET_FACEBOOK_URLS=https://www.facebook.com/example_rescue_page
CHECK_INTERVAL_MINUTES=15
""",

    ".gitignore": """__pycache__/
*.pyc
.env
venv/
*.mp3
*.wav
*.m4a
.DS_Store
""",

    "Dockerfile": """FROM python:3.11-slim

RUN apt-get update && \\
    apt-get install -y --no-install-recommends ffmpeg && \\
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
""",

    "docker-compose.yml": """version: '3.8'

services:
  flood-detector:
    build: .
    container_name: flood_distress_detector
    restart: unless-stopped
    env_file:
      - .env
""",

    "README.md": """# 🌊 Flood Distress Detector

เครื่องมือ Open-source คัดกรองและสกัดข้อมูลเคสขอความช่วยเหลือเหตุน้ำท่วมจาก Social Media ด้วย AI (Whisper + LLM) และแจ้งเตือนทีมกู้ภัยผ่าน Telegram

## 🚀 เริ่มต้นใช้งาน

1. คัดลอก Environment file:
   ```bash
   cp .env.example .env
   ```
2. แก้ไข API Keys ต่างๆ ในไฟล์ `.env`
3. สั่งรันด้วย Docker Compose:
   ```bash
   docker compose up -d --build
   ```
""",

    "main.py": """import os
import time
import tempfile
from dotenv import load_dotenv
from openai import OpenAI
from apify_client import ApifyClient

from src.fetcher import fetch_target_posts
from src.audio import extract_audio
from src.transcriber import transcribe_audio
from src.extractor import analyze_text
from src.notifier import send_alert

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TARGET_URLS = [u.strip() for u in os.getenv("TARGET_FACEBOOK_URLS", "").split(",") if u.strip()]
INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))

apify_client = ApifyClient(APIFY_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)
processed_post_ids = set()

def run_pipeline():
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] กำลังเริ่มรอบการตรวจจับ...")
    for page_url in TARGET_URLS:
        print(f">> ตรวจสอบเพจ: {page_url}")
        posts = fetch_target_posts(apify_client, page_url, max_posts=5)
        
        for post in posts:
            post_id = post["post_id"]
            if post_id in processed_post_ids:
                continue
            
            processed_post_ids.add(post_id)
            print(f"-> ตรวจพบโพสต์ใหม่: {post['url']}")
            combined_context = f"Caption: {post['caption']}"
            
            if post["video_url"]:
                with tempfile.TemporaryDirectory() as temp_dir:
                    audio_path = os.path.join(temp_dir, "temp_audio")
                    expected_mp3 = f"{audio_path}.mp3"
                    if extract_audio(post["video_url"], audio_path):
                        transcription = transcribe_audio(expected_mp3, openai_client)
                        if transcription:
                            combined_context += f"\\nVideo Audio: {transcription}"

            report = analyze_text(combined_context, openai_client)
            if report.is_distress:
                print(f"🚨 พบเคสขอความช่วยเหลือ! ระดับ: {report.urgency}")
                send_alert(report, post["url"], TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
            else:
                print("ℹ️ ไม่ใช่การขอความช่วยเหลือฉุกเฉิน")

def main():
    if not all([APIFY_TOKEN, OPENAI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
        raise ValueError("กรุณากรอก Environment Variables ในไฟล์ .env ให้ครบถ้วน")
        
    print("เริ่มการทำงานของระบบ Flood Distress Detector...")
    while True:
        try:
            run_pipeline()
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการทำงาน: {e}")
        time.sleep(INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main()
""",

    "src/__init__.py": "",

    "src/fetcher.py": """from apify_client import ApifyClient

def fetch_target_posts(client: ApifyClient, page_url: str, max_posts: int = 5) -> list[dict]:
    run_input = {
        "startUrls": [{"url": page_url}],
        "resultsLimit": max_posts,
    }
    try:
        run = client.actor("apify/facebook-posts-scraper").call(run_input=run_input)
        posts = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            posts.append({
                "post_id": item.get("id") or item.get("url"),
                "url": item.get("url") or item.get("postUrl"),
                "caption": item.get("text", ""),
                "video_url": item.get("media", [{}])[0].get("url") if item.get("media") else None
            })
        return posts
    except Exception as e:
        print(f"ดึงข้อมูล Facebook ไม่สำเร็จ: {e}")
        return []
""",

    "src/audio.py": """import yt_dlp

def extract_audio(video_url: str, output_path: str) -> bool:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return True
    except Exception as e:
        print(f"ไม่สามารถดาวน์โหลดเสียงจากวิดีโอได้: {e}")
        return False
""",

    "src/transcriber.py": """import os
from openai import OpenAI

def transcribe_audio(audio_file_path: str, client: OpenAI) -> str:
    if not os.path.exists(audio_file_path):
        return ""
    try:
        with open(audio_file_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="th"
            )
        return transcript.text
    except Exception as e:
        print(f"ถอดเสียงไม่สำเร็จ: {e}")
        return ""
""",

    "src/extractor.py": """from pydantic import BaseModel, Field
from openai import OpenAI

class DistressReport(BaseModel):
    is_distress: bool = Field(description="เป็นโพสต์ขอความช่วยเหลือเหตุน้ำท่วมจริงหรือไม่")
    urgency: str = Field(description="ระดับความด่วน: CRITICAL, HIGH, MEDIUM, LOW")
    location: str = Field(description="พิกัด หมู่บ้าน ตำบล อำเภอ หรือจุดสังเกต")
    contact: str = Field(description="เบอร์โทรศัพท์ หรือชื่อผู้ติดต่อ")
    needs: list[str] = Field(description="สิ่งที่ต้องการ เช่น ข้าวสาร น้ำดื่ม เรือ อพยพคนแก่")
    summary: str = Field(description="สรุปเหตุการณ์ 1 ประโยค")

def analyze_text(text: str, client: OpenAI) -> DistressReport:
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "คุณคือ AI กู้ภัย มีหน้าที่คัดกรองเคสขอความช่วยเหลือเหตุน้ำท่วมจากข้อความ"},
            {"role": "user", "content": text},
        ],
        response_format=DistressReport,
    )
    return completion.choices[0].message.parsed
""",

    "src/notifier.py": """import requests

def send_alert(report, source_url: str, bot_token: str, chat_id: str):
    if not report.is_distress:
        return

    urgency_tag = {
        "CRITICAL": "🚨 วิกฤตด่วนที่สุด",
        "HIGH": "🔴 ด่วนมาก",
        "MEDIUM": "🟡 ปานกลาง",
        "LOW": "🟢 ทั่วไป"
    }.get(report.urgency, "⚠️ แจ้งเหตุ")

    needs_text = ", ".join(report.needs) if report.needs else "ไม่ระบุ"
    message = (
        f"{urgency_tag} (ตรวจพบเคสน้ำท่วม)\\n"
        f"━━━━━━━━━━━━━━━━━━\\n"
        f"📍 พื้นที่: {report.location}\\n"
        f"📞 ติดต่อ: {report.contact}\\n"
        f"📦 ต้องการ: {needs_text}\\n"
        f"📝 สรุป: {report.summary}\\n"
        f"🔗 ลิงก์ต้นทาง: {source_url}"
    )

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=10)
    except Exception as e:
        print(f"ส่ง Telegram ไม่สำเร็จ: {e}")
"""
}

# 2. ทำการสร้าง Zip File
ZIP_NAME = "flood-distress-detector.zip"

with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zf:
    for filepath, content in PROJECT_FILES.items():
        zf.writestr(filepath, content.strip() + "\n")
        print(f"เพิ่มไฟล์: {filepath}")

print(f"\nสร้างไฟล์ {ZIP_NAME} สำเร็จเรียบร้อยแล้ว!")
```

เมื่อรันเสร็จ จะได้ไฟล์ `flood-distress-detector.zip` อยู่ในโฟลเดอร์เดียวกันทันที สามารถนำไปแตกไฟล์หรืออัปโหลดเข้า GitHub Repository ได้โดยตรง

---

# you asked

message time: 2026-09-30 16:16:28

สรุปชุด code นี้ทำอะไรได้บ้าง

---

# gemini response

ชุดโค้ดนี้คือ **ระบบเฝ้าระวังและคัดกรองผู้ประสบภัยน้ำท่วมอัตโนมัติแบบครบวงจร (Automated Flood Distress Pipeline)** ที่ทำงานตั้งแต่ต้นน้ำจนถึงปลายน้ำ โดยมีความสามารถหลัก 5 ด้าน:

---

### 1. ดึงโพสต์และวิดีโอจาก Facebook อัตโนมัติ (`fetcher.py`)
* วนลูปตรวจสอบเพจเป้าหมาย (เช่น เพจข่าวท้องถิ่น, ศูนย์กู้ภัย) ผ่าน Apify Scraper API ทุกๆ X นาทีตามที่ตั้งไว้
* ดึงทั้งข้อความแคปชัน (Caption) และลิงก์วิดีโอ (Video URL)
* มีระบบจำกัดการอ่านโพสต์ซ้ำ (`processed_post_ids`) ไม่ให้ดึงข้อมูลเดิมมาประมวลผลซ้ำ

### 2. สกัดเสียงและถอดเป็นข้อความภาษาไทย (`audio.py`, `transcriber.py`)
* ใช้ `yt-dlp` ดาวน์โหลดเฉพาะแทร็กเสียงจากคลิปวิดีโอมาเป็นไฟล์ `.mp3` ชั่วคราว (ประหยัดแบนด์วิดท์ ไม่โหลดภาพวิดีโอ)
* ส่งไฟล์เสียงเข้า **OpenAI Whisper API** เพื่อถอดเสียงพูดภาษาไทยในคลิปออกมาเป็นข้อความตัวหนังสือ

### 3. คัดกรองและสกัดข้อมูลสำคัญด้วย AI (`extractor.py`)
* นำทั้งแคปชันและข้อความที่ถอดได้จากเสียง ส่งให้ **LLM (`gpt-4o-mini`)** วิเคราะห์
* ใช้ **Structured Outputs (Pydantic)** บังคับคำตอบให้ออกมาเป็นฟิลด์ข้อมูลที่แน่นอน:
  * **ตรวจสอบ:** เป็นเคสขอความช่วยเหลือจริงหรือไม่ (`is_distress`) ป้องกันการแจ้งเตือนมั่วจากคลิปข่าวทั่วไป
  * **ระดับความเร่งด่วน:** แบ่งเป็น `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`
  * **พิกัดสถานที่:** คัดเฉพาะชื่อหมู่บ้าน ตำบล อำเภอ หรือจุดสังเกต
  * **เบอร์ติดต่อ:** ดึงเบอร์โทรศัพท์หรือชื่อผู้แจ้ง
  * **สิ่งที่ต้องการ:** สรุปเป็นรายการ เช่น อาหาร น้ำดื่ม ยารักษาโรค เรืออพยพผู้ป่วย

### 4. ส่งแจ้งเตือนฉุกเฉินเข้า Telegram ทันที (`notifier.py`)
* เมื่อ AI ตรวจพบว่าเป็นเคสเดือดร้อนจริง จะจัด Format ข้อความให้อ่านง่าย มีอีโมจิบ髮งระดับความเร่งด่วน พิกัด และลิงก์โพสต์ต้นทาง
* ส่งตรงเข้าห้องแชตหรือกลุ่มของทีมกู้ภัย/จิตอาสาผ่าน **Telegram Bot API** ทันทีแบบ Real-time

### 5. รองรับการ Deploy และแจกจ่าย (`Dockerfile`, `docker-compose.yml`)
* บรรจุสภาพแวดล้อมที่จำเป็น (รวมถึง `ffmpeg`) ไว้ใน Docker
* ผู้ใช้อื่นสามารถโคลนจาก GitHub แล้วสั่ง `docker compose up -d` ให้ระบบรันเป็น Background Service ทำงาน 24 ชม. ได้ทันทีโดยไม่ต้องลง Environment ในเครื่องให้ยุ่งยาก

---

# you asked

message time: 2026-09-30 16:18:52

แล้ว สมมติ ผมอยากจะรู่เช่น จังหวัด ปราจีน มีคนพูดถึงใน social ตรงไหนมากที่สุด จะรู้ได้ไหม หรือมันดึงเองไปทั่ว เพราะ มันจะมีเพจข่าว ด้วย ผมไม่แน่ใจควรจะดึงจากเพจข่าวหรือเปล่า เพราะ คนใน social เร็วกว่า และเพจข่าวจะออกซ้ำ หรือเราควรจะเอาจากข่าว ด้วยไหม ข่าวก็มีไป interview

---

# gemini response

คำถามนี้ตรงจุดยุทธศาสตร์ของระบบ Social Listening และกู้ภัยมาก เพราะระหว่าง **"เสียงจากชาวบ้านจริง"** กับ **"เพจข่าว"** มีข้อดี-ข้อเสียต่างกันอย่างชัดเจน

---

### 1. จะรู้ได้อย่างไรว่า "ปราจีนบุรี" มีคนพูดถึงตรงไหนมากที่สุด?

หากต้องการรู้จุดที่มีการพูดถึงหนาแน่นที่สุด (Heatmap / Hotspot) ระบบจะไม่ดึงไปเรื่อยๆ ทั่วประเทศ แต่จะใช้เทคนิค **Location Mention Aggregation**:

* **จับคู่ชื่อภูมิศาสตร์ (Named Entity Recognition - NER):**
  * ให้ระบบมีฐานข้อมูลตำบลและอำเภอของปราจีนบุรีเตรียมไว้ (เช่น *กบินทร์บุรี, นาดี, ศรีมหาโพธิ, ประจันตคาม, บ้านสร้าง, กบินทร์, ลาดตะเคียน*)
  * เมื่อ AI ถอดข้อความ (จากทั้งแคปชันและคลิป) ให้สกัดชื่อ "ตำบล/หมู่บ้าน/อำเภอ" ออกมา
* **นับความถี่ (Count & Cluster):**
  * สร้างตัวแปรนับจำนวนการกล่าวถึงต่อพื้นที่ เช่น:
    * `กบินทร์บุรี`: 45 เคส
    * `ศรีมหาโพธิ`: 12 เคส
    * `บ้านสร้าง`: 3 เคส
  * ทำให้เห็นทันทีว่าขณะนี้จุดศูนย์กลางวิกฤต (Epicenter) อยู่ที่อำเภอหรือตำบลใด

---

### 2. ควรดึงจาก "เพจข่าว" หรือ "คนใน Social ทั่วไป"?

**คำตอบคือ ควรดึงทั้ง 2 ทาง แต่ให้แบ่งหน้าที่ (Weight & Role) ชัดเจน:**

| มิติ | คนใน Social (TikTok / FB Groups ท้องถิ่น) | เพจข่าว / สื่อท้องถิ่น |
| :--- | :--- | :--- |
| **ความเร็ว** | ⚡ **เร็วที่สุด (Real-time)** ชาวบ้านโพสต์ตอนน้ำเริ่มแตะขอบประตูบ้าน | ⏳ ช้ากว่า 1–3 ชม. ต้องรอทีมงานตัดต่อ/เขียนข่าว |
| **ความแม่นยำของพิกัด** | ⚠️ มักบอกจุดสังเกตเฉพาะถิ่น เช่น *"ซอยข้างวัดบางกระเบา"* | ✅ มักระบุข้อมูลทางการครบ เช่น *"ม.3 ต.บ้านสร้าง อ.บ้านสร้าง"* |
| **ความลึกของข้อมูล** | ❌ มักเป็นคลิปสั้น ไม่ระบุจำนวนคนหรือเบอร์ติดต่อ | ✅ มีการสัมภาษณ์ชาวบ้าน ทำให้รู้ว่า *"มีติดอยู่ 5 คน มีคนแก่ป่วยติดเตียง"* |
| **ปัญหาข้อมูลซ้ำ** | มีบ้างหากเป็นคลิปไวรัล | ⚠️ **ซ้ำสูงมาก** ข่าวสำนักต่างๆ มักแชร์เคสเดียวกัน |

---

### 3. กลยุทธ์ในการจัดสถาปัตยกรรมข้อมูล (Data Strategy)

เพื่อไม่ให้ระบบรกด้วยข่าวซ้ำ และไม่พลาดเสียงด่วนจากชาวบ้าน:

#### ก. แหล่งที่ควรเล็งเป้า (Target Sources)
1. **TikTok Search / Hashtag:** `#น้ำท่วมปราจีน`, `#กบินทร์บุรี` (ได้คลิป Real-time จากชาวบ้านโดยตรง)
2. **กลุ่มสาธารณะประจำพื้นที่ (Community Groups):** ไม่ใช่เพจข่าวใหญ่ แต่เป็นกลุ่มอย่าง *"กลุ่มแจ้งข่าวชาวกบินทร์"*, *"คนเมืองปราจีน"* ซึ่งชาวบ้านใช้โพสต์ขอความช่วยเหลือกันเอง
3. **เพจข่าวท้องถิ่นเฉพาะจังหวัด:** (เช่น *"ข่าวปราจีนบุรีนิวส์"*, *"สมาคมกู้ภัยสว่างบำเพ็ญธรรมสถาน"*) คัดไว้เพียง 2–3 เพจหลัก ไม่ต้องดึงทุกสำนักข่าว เพื่อเลี่ยงข้อมูลซ้ำ

#### ข. ระบบตัดข้อมูลซ้ำ (Deduplication Layer) ด้วย LLM
เมื่อเพจข่าวและชาวบ้านพูดถึงเรื่องเดียวกัน ป้องกันการแจ้งเตือนซ้ำโดยส่งพิกัดและเคสให้ LLM เช็กก่อนส่งแจ้งเตือน:

```text
Prompt เสริมสำหรับตรวจสอบความซ้ำซ้อน:
"มีเคสก่อนหน้านี้รายงานว่า: 'คนแก่อยู่บ้านเลขที่ 12 หมู่ 3 กบินทร์บุรี ติดน้ำท่วม'
เคสใหม่ที่กำลังอ่านคือ: 'นักข่าวสัมภาษณ์คุณยายหมู่ 3 กบินทร์บุรี น้ำท่วมมิดชั้น 1'
คำถาม: สองข้อความนี้คือเคสเดียวกันหรือไม่? (Yes/No)"
```

* ถ้าเป็น **Yes (เคสเดียวกัน):** ให้ระบบนำข้อมูลสัมภาษณ์ของข่าวไป "อัปเดตรายละเอียดเพิ่มเติม" ให้เคสเดิม แทนที่จะแจ้งเตือนเป็นเคสใหม่
* ถ้าเป็น **No (คนละจุด):** ปล่อยแจ้งเตือนเป็นเคสใหม่ทันที

แนวทางนี้จะช่วยให้รู้ทั้ง **พิกัดที่กำลังวิกฤตที่สุด** อย่างรวดเร็วจากคนในพื้นที่ และได้ **รายละเอียดเชิงลึก** จากการสัมภาษณ์ของนักข่าวโดยไม่ถูกสแปมด้วยข่าวซ้ำ

---

# you asked

message time: 2026-09-30 16:25:15

ช่วยคิดหน่อยทคือ ผมอยากจะทำ code ให้เขารัน และให้เขาำรองมาจาก vdo social  เป็นข้อมูลส่วนกลาง , อีกส่วนหนึ่ง อยากจะให้ค้นหา แล้วเจอตรงไหนบ้าง เช่นให้ตัวแทนในจังหวัดนั้นๆ หรือเขต นั้น กรณีเป็น กทม จะได้บอกกุ้ภัยให้ไปตำบลนั้นๆ

---

# gemini response

โจทย์นี้คือการยกระดับจาก Script เดี่ยวๆ ให้กลายเป็น **"ระบบเครือข่ายข้อมูลภัยพิบัติแบบกระจายศูนย์ (Crowdsourced Flood Hub)"** 

แนวคิดคือให้คนในพื้นที่ (Node) รันบอทดึงวิดีโอ/เสียงในเขตตัวเอง แล้วส่งข้อมูลดิบเข้ามาประมวลผลที่ **ฐานข้อมูลกลาง (Central Database)** จากนั้นเปิดช่องทางให้ตัวแทนจังหวัด/กู้ภัยในเขตต่างๆ เข้ามาค้นหาหรือรับแจ้งเตือนเฉพาะพื้นที่ของตนเองได้ทันที

---

### 1. สถาปัตยกรรมระบบโดยรวม (System Architecture)

```text
[อาสาสมัครรัน Node พื้นที่ A, B, C]
    │ (ดึงคลิป TikTok / FB ในเขตตัวเอง)
    ▼
[STT (Whisper) + LLM Normalizer] ───► แปลงชื่อพื้นที่เป็น Standard Format
    │
    ▼
[ฐานข้อมูลกลาง (Supabase / PostgreSQL + PostGIS)]
    │
    ├─► [API ค้นหาตามพิกัด/เขต/ตำบล] ────► [หน้า Web Dashboard สำหรับทีมกู้ภัย]
    │
    └─► [Telegram Bot แยกห้องตามจังหวัด/เขต] ──► แจ้งเตือนตรงเข้ากลุ่มกู้ภัยประจำพื้นที่
```

---

### 2. การจัดโครงสร้างข้อมูลกลาง (Data Schema)

หัวใจสำคัญที่ทำให้ค้นหาเจอง่าย คือการทำ **Data Normalization** แปลงชื่อเล่นของสถานที่ให้กลายเป็นฟิลด์ทางการ (`province`, `district`, `subdistrict`):

```json
{
  "incident_id": "uuid-v4",
  "timestamp": "2026-09-30T16:30:00Z",
  "province": "ปราจีนบุรี",
  "district": "กบินทร์บุรี",
  "subdistrict": "กบินทร์",
  "landmark_raw": "ซอยข้างวัดบางกระเบา",
  "urgency": "CRITICAL",
  "needs": ["เรือพาย", "ยารักษาโรค", "อพยพผู้ป่วยติดเตียง"],
  "headcount": 4,
  "contact": "081-xxx-xxxx",
  "source_platform": "TikTok",
  "source_url": "https://...",
  "status": "OPEN", // OPEN, IN_PROGRESS, RESOLVED
  "assigned_team": null
}
```

> **เทคนิคสำคัญ:** ในขั้นตอนนี้ให้ LLM จับคู่ชื่อสถานที่เข้ากับฐานข้อมูลตำบล/อำเภอทางการของกรมการปกครอง (DOPA) หากเป็น กทม. ให้จับคู่เป็น `เขต` และ `แขวง` แทน

---

### 3. ส่วนประกอบที่ต้องสร้างเพิ่ม (Core Components)

#### ก. ฝั่ง Node ส่งข้อมูล (Contributor Node)
อาสาสมัครในแต่ละพื้นที่รัน Script คอยดึงวิดีโอ เมื่อถอดเสียงและสกัดข้อมูลแล้ว ให้ยิง POST เข้าสู่ REST API กลาง:

```python
import requests

CENTRAL_API_URL = "https://your-central-flood-hub.com/api/reports"
NODE_API_KEY = "NODE_AUTH_KEY_XXXX"

def push_to_central_hub(distress_data: dict):
    headers = {"Authorization": f"Bearer {NODE_API_KEY}"}
    response = requests.post(CENTRAL_API_URL, json=distress_data, headers=headers)
    return response.status_code == 201
```

#### ข. ฝั่งค้นหาและกรองข้อมูลสำหรับกู้ภัย (Rescue Filtering System)
สร้าง Endpoint หรือฟังก์ชันเพื่อให้ทีมหน้างานดึงข้อมูลเฉพาะโซนที่ตนเองรับผิดชอบ:

* **ค้นหาตามชื่อพื้นที่:** ค้นหาด้วยคำว่า `กบินทร์บุรี` หรือ `เขตดอนเมือง`
* **ตัวอย่าง REST API Endpoints:**
  * `GET /api/reports?province=ปราจีนบุรี&district=กบินทร์บุรี&status=OPEN`
  * `GET /api/reports?province=กรุงเทพมหานคร&district=สายไหม&urgency=CRITICAL`

#### ค. การกระจายข่าวตรงกลุ่ม (Targeted Dispatcher)
แทนที่จะส่งทุกเรื่องเข้าห้องรวมห้องเดียว ให้แยกการแจ้งเตือนตามพื้นที่:

* **วิธีที่ 1: Telegram Topics (Forum Groups)** 
  * สร้าง 1 Supergroup ชื่อ "ศูนย์แจ้งเหตุฉุกเฉินน้ำท่วม"
  * ภายในแบ่ง Topic เป็นชื่อจังหวัดหรือเขต เช่น `#ปราจีนบุรี`, `#เชียงราย`, `#กทม-โซนเหนือ`
  * บอทจะยิงแจ้งเตือนเข้าเฉพาะ Topic นั้นๆ กู้ภัยในพื้นที่แค่เข้าไปติดตาม Topic ของตัวเอง
* **วิธีที่ 2: Telegram Bot แบบสั่งค้นหาได้ (`/search`)**
  * เจ้าหน้าที่กู้ภัยพิมพ์สั่งบอทในแชต:
    ```text
    /find กทม บางเขน
    /find ปราจีน กบินทร์
    ```
  * บอทจะตอบกลับรายการเคสที่สถานะเป็น `OPEN` และด่วนที่สุด 5 อันดับแรกพร้อมเบอร์ติดต่อทันที

---

### 4. แผนการเริ่มพัฒนาทีละสเต็ป (Step-by-step Execution)

1. **ใช้ Supabase เป็น Backend สำเร็จรูป (ฟรีและเร็วสุด):**
   * ได้ฐานข้อมูล PostgreSQL ทันที
   * มี REST API สร้างให้อัตโนมัติโดยไม่ต้องเขียน Backend เอง
   * มีฟังก์ชัน Realtime Database รองรับการอัปเดตสถานะเคส (เช่น กู้ภัยกดปุ่ม "รับเคสนี้แล้ว" หน้าจอจะเปลี่ยนสีทันที)
2. **สร้าง Telegram Search Command:** ทำบอทให้ตอบรับคำสั่ง `/check [ชื่อตำบล/อำเภอ]` เพื่อให้ทีมอาสาค้นหาได้จากมือถือทันทีโดยไม่ต้องเปิดคอมพิวเตอร์
3. **ทำหน้าเว็บดูแผนที่ Heatmap (ต่อยอด):** แสดงหมุดเคสที่รอความช่วยเหลือ โดยแบ่งสีตามระดับความวิกฤต (แดง = ด่วนที่สุด, เหลือง = ปานกลาง)

<ElicitationsGroup message="ต้องการเริ่มขยายระบบในส่วนใดก่อน:">
  <Elicitation label="ดูตัวอย่าง SQL Schema และการเชื่อมต่อ Supabase" query="ขอตัวอย่างโครงสร้างฐานข้อมูล SQL บน Supabase และโค้ด Python สำหรับส่งและค้นหาข้อมูลผู้ประสบภัย"/>
  <Elicitation label="เขียนคำสั่ง Telegram Bot ให้กู้ภัยค้นหาเคสตามพื้นที่" query="ขอโค้ด Telegram Bot ที่รองรับคำสั่ง /search สำหรับให้กู้ภัยค้นหาเคสผู้ประสบภัยตามอำเภอหรือเขต"/>
  <Elicitation label="ปรับ Prompt ให้ LLM แปลงชื่อสถานที่ให้ตรงกับมาตรฐาน DOPA" query="ขอ Prompt สำหรับ LLM เพื่อทำ Normalization ชื่อหมู่บ้าน ชุมชน ตำบล อำเภอ ในไทยให้เป็นมาตรฐาน"/>
</ElicitationsGroup>

---

# you asked

message time: 2026-09-30 16:29:24

ขอ Prompt สำหรับ LLM เพื่อทำ Normalization ชื่อหมู่บ้าน ชุมชน ตำบล อำเภอ ในไทยให้เป็นมาตรฐาน

---

# gemini response

หัวใจสำคัญของการแปลงชื่อสถานที่ไทย (Entity Normalization) คือการจัดการ **ชื่อย่อ, ภาษาพูด, การตัดคำนำหน้า (ต./อ./จ.), และความแตกต่างของเขตการปกครองระหว่าง กทม. (แขวง/เขต) กับ ต่างจังหวัด (ตำบล/อำเภอ)**

นี่คือ System Prompt และโครงสร้าง Pydantic พร้อมตัวอย่างใช้งานจริง

---

### 1. System Prompt สำหรับ LLM

```text
คุณคือระบบสกัดและปรับมาตรฐานข้อมูลพิกัดภูมิศาสตร์ไทย (Thai Administrative Geography Normalizer) สำหรับงานกู้ภัยฉุกเฉิน

หน้าที่ของคุณ:
วิเคราะห์ข้อความหรือคำพูดภาษาถิ่น แล้วแปลงพิกัดสถานที่ให้ตรงตามโครงสร้างทางการของกรมการปกครอง (DOPA)

กฎเกณฑ์ในการประมวลผล (Strict Rules):
1. กรณีเป็นกรุงเทพมหานคร:
   - province ต้องเป็น "กรุงเทพมหานคร" (ห้ามใช้คำย่อ เช่น กทม.)
   - district คือ "เขต" (ตัดคำว่า 'เขต' ออก ใส่เฉพาะชื่อ เช่น "สายไหม", "ดอนเมือง")
   - subdistrict คือ "แขวง" (ตัดคำว่า 'แขวง' ออก ใส่เฉพาะชื่อ เช่น "คลองถนน")
2. กรณีเป็นต่างจังหวัด:
   - province คือ "จังหวัด" (ตัดคำว่า 'จังหวัด' ออก เช่น "ปราจีนบุรี", "เชียงราย")
   - district คือ "อำเภอ" (ตัดคำว่า 'อำเภอ/อ.' ออก เช่น "กบินทร์บุรี", "แม่สาย")
   - subdistrict คือ "ตำบล" (ตัดคำว่า 'ตำบล/ต.' ออก เช่น "เมืองเก่า", "เวียงพางคำ")
3. การจัดการชื่อย่อและภาษาพูด:
   - ขยายชื่อย่อให้เต็มเสมอ เช่น "โคราช" -> "นครราชสีมา", "แปดริ้ว" -> "ฉะเชิงเทรา", "แม่สาย" -> อำเภอ "แม่สาย" จังหวัด "เชียงราย"
   - หากผู้พูดระบุเฉพาะชื่ออำเภอที่มีชื่อเสียงและบริบทชัดเจน ให้เติมจังหวัดที่ถูกต้องลงไป
4. รายละเอียดเจาะจง (Landmark & Village):
   - แยก "หมู่บ้าน/ชุมชน/หมู่ที่/ซอย/ถนน/จุดสังเกตเฉพาะ" ไปใส่ใน village_or_community หรือ landmark_detail ห้ามนำมาปนกับ subdistrict/district
5. ความไม่แน่นอน:
   - หากระบุไม่ชัดเจนหรือไม่มีข้อมูลในระดับใด ให้ใส่ null
   - ประเมิน confidence_score (0.0 - 1.0) ว่าข้อมูลพิกัดมีความน่าเชื่อถือเพียงใด
```

---

### 2. โค้ด Python (Structured Outputs ด้วย Pydantic)

ใช้ฟีเจอร์ Structured Outputs ของ OpenAI หรือ Gemini เพื่อบังคับให้ออกผลลัพธ์เป็น JSON Schema ที่ถูกต้อง 100%:

```python
from typing import Optional
from pydantic import BaseModel, Field
from openai import OpenAI

class NormalizedLocation(BaseModel):
    is_bangkok: bool = Field(description="จริงหากเป็นพื้นที่ในกรุงเทพมหานคร")
    province: Optional[str] = Field(description="ชื่อจังหวัดเต็ม เช่น 'ปราจีนบุรี', 'กรุงเทพมหานคร' (ไม่มีคำว่า จังหวัด)")
    district: Optional[str] = Field(description="ชื่ออำเภอ หรือ เขต (ไม่มีคำว่า อำเภอ หรือ เขต)")
    subdistrict: Optional[str] = Field(description="ชื่อตำบล หรือ แขวง (ไม่มีคำว่า ตำบล หรือ แขวง)")
    village_or_community: Optional[str] = Field(description="หมู่ที่, ชื่อหมู่บ้าน, หรือชื่อชุมชน เช่น 'หมู่ 3 บ้านท่าลาน', 'ชุมชนริมคลอง'")
    landmark_detail: Optional[str] = Field(description="จุดสังเกต ซอย ถนน หรือสถานที่ใกล้เคียง เช่น 'ซอยข้างวัดบางกระเบา', 'ตรงข้ามโรงเรียน'")
    confidence_score: float = Field(description="ระดับความมั่นใจของพิกัด 0.0 ถึง 1.0")

def extract_normalized_location(text: str, client: OpenAI) -> NormalizedLocation:
    system_prompt = """คุณคือระบบสกัดและปรับมาตรฐานข้อมูลพิกัดภูมิศาสตร์ไทย (DOPA Standard) สำหรับงานกู้ภัยฉุกเฉิน
แปลงชื่อย่อ ภาษาถิ่น และจุดสังเกตให้เข้าสู่โครงสร้างที่กำหนดอย่างเคร่งครัด"""

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"ข้อความแจ้งเหตุ: {text}"},
        ],
        response_format=NormalizedLocation,
    )
    return completion.choices[0].message.parsed
```

---

### 3. ตัวอย่างการแปลงผลลัพธ์ (Input -> Output)

#### ตัวอย่างที่ 1: ภาษาพูดต่างจังหวัด + ชื่อย่อ
* **ข้อความดิบ:** *"น้ำเอ่อล้นตลิ่งแล้ว ตอนนี้ติดอยู่หมู่ 4 บ้านวังหิน ต.กบินทร์ แถวๆ กบินทร์บุรี ปราจีน ช่วยด้วยครับ"*
* **ผลลัพธ์ JSON:**
```json
{
  "is_bangkok": false,
  "province": "ปราจีนบุรี",
  "district": "กบินทร์บุรี",
  "subdistrict": "กบินทร์",
  "village_or_community": "หมู่ 4 บ้านวังหิน",
  "landmark_detail": "ใกล้แม่น้ำเอ่อล้นตลิ่ง",
  "confidence_score": 0.98
}
```

#### ตัวอย่างที่ 2: เขตกรุงเทพมหานคร + จุดสังเกต
* **ข้อความดิบ:** *"ซอยรามอินทรา 39 แขวงท่าแร้ง บางเขน กทม น้ำท่วมสูงครึ่งคันรถแล้ว สัญจรไม่ได้"*
* **ผลลัพธ์ JSON:**
```json
{
  "is_bangkok": true,
  "province": "กรุงเทพมหานคร",
  "district": "บางเขน",
  "subdistrict": "ท่าแร้ง",
  "village_or_community": null,
  "landmark_detail": "ซอยรามอินทรา 39",
  "confidence_score": 0.99
}
```

#### ตัวอย่างที่ 3: ระบุแค่ชื่อสถานที่/อำเภอดัง (Implicit Location)
* **ข้อความดิบ:** *"ติดอยู่แถวตลาดเกาะทราย แม่สาย น้ำเชี่ยวมาก ออกไม่ได้"*
* **ผลลัพธ์ JSON:**
```json
{
  "is_bangkok": false,
  "province": "เชียงราย",
  "district": "แม่สาย",
  "subdistrict": "เวียงพางคำ",
  "village_or_community": "ตลาดเกาะทราย",
  "landmark_detail": null,
  "confidence_score": 0.85
}
```

---

### 4. ข้อดีเมื่อนำไปเก็บในฐานข้อมูล (Database Query)
เมื่อฟิลด์ถูกตัดแต่งจนเป็นมาตรฐาน (Standardized) ทีมกู้ภัยสามารถรันคำสั่งค้นหาแบบตรงไปตรงมาได้ทันที เช่น:
```sql
-- ค้นหาเคสทั้งหมดในอำเภอกบินทร์บุรี
SELECT * FROM flood_reports 
WHERE province = 'ปราจีนบุรี' AND district = 'กบินทร์บุรี' AND status = 'OPEN';
```
หมดปัญหาเรื่องการค้นหาคำไม่เจอจากกรณีที่บางคนพิมพ์ "อ.กบินทร์", "กบินทร์บุรี", หรือ "ต.กบินทร์" สลับกัน

<FollowUp label="ต้องการดูวิธีเชื่อมต่อผลลัพธ์นี้ลงฐานข้อมูล Supabase เพื่อทำหน้าตารางกู้ภัยไหม?" query="ขอโค้ด Python สำหรับนำข้อมูล NormalizedLocation ที่ได้นี้บันทึกลงตารางใน Supabase พร้อมตัวอย่างคำสั่ง SQL สร้าง Table"/>

---

# you asked

message time: 2026-09-30 16:29:40

ผมจะต้องมีที่เก็บ DB ด้วยใช่ไหม

---

# gemini response

**ใช่ครับ จำเป็นต้องมี DB อย่างแน่นอน** หากต้องการให้ระบบทำงานได้จริง ไม่ใช่แค่บอทแจ้งเตือนแบบผ่านแล้วผ่านเลย

สาเหตุหลัก 4 ข้อที่ต้องมี DB คือ:

1. **ป้องกันการแจ้งเตือนซ้ำ (Deduplication):** ถ้าไม่มี DB จำ `post_id` หรือเนื้อหา บอทจะวนไปอ่านโพสต์เดิมทุกรอบที่รัน และส่งแจ้งเตือนซ้ำๆ เข้ากลุ่มกู้ภัยจนกลายเป็นสแปม
2. **ตัวกลางเชื่อมโยงหลายคน (Centralized Node):** คนรันตัวสแกนอาจมีหลายคน (เช่น นาย A สแกน TikTok, นาย B สแกน Facebook) ทั้งหมดต้องยิงข้อมูลมารวมไว้ที่เดียวกัน
3. **ติดตามสถานะเคสกู้ภัย (Case Status):** กู้ภัยจำเป็นต้องมีช่องเปลี่ยนสถานะ เช่น `รอดำเนินการ` -> `ทีมสว่างฯ กำลังเข้าช่วยเหลือ` -> `ช่วยเหลือสำเร็จแล้ว` หากไม่มี DB จะไม่สามารถบันทึกสถานะเหล่านี้ได้
4. **ค้นหาและจัดลำดับความเร่งด่วน:** ให้กู้ภัยสามารถ Filter ค้นหาเฉพาะ `"อำเภอกบินทร์บุรี ที่ยังไม่ได้รับความช่วยเหลือ และเป็นเคสด่วนสุด"` ได้ทันที

---

### ไม่ต้องตั้ง Server เอง: ตัวเลือก DB แนะนำสำหรับเริ่มงานกู้ภัย

เพื่อความรวดเร็วและประหยัดงบ ไม่จำเป็นต้องเช่า VPS หรือติดตั้ง MySQL/PostgreSQL เอง มี 2 ทางเลือกที่สะดวกที่สุด:

| ทางเลือก | ข้อดี | เหมาะสำหรับ | ความง่าย |
| :--- | :--- | :--- | :--- |
| **Supabase (แนะนำที่สุด)** | • เป็น PostgreSQL บน Cloud<br>• มี Free Tier เหลือเฟือสำหรับภัยพิบัติ<br>• ได้ **REST API ทันที** ไม่ต้องเขียน Backend<br>• มีหน้า Dashboard ให้คนทั่วไปเปิดดู/แก้สถานะเคสได้เหมือน Excel | ระบบที่ต้องการความเสถียร มีระบบ Filter ตำบล/อำเภอ แม่นยำ และต้องการทำ Dashboard ในอนาคต | ⭐⭐⭐⭐ (ปานกลาง) |
| **Google Sheets (ผ่าน `gspread`)** | • ทุกคนในทีมกู้ภัยใช้เป็นทันทีโดยไม่ต้องสอน<br>• ฟรี 100% | เริ่มต้นทดสอบวันแรก ต้องการให้ทีมอาสาเปิดดูผ่านมือถือได้ง่ายที่สุด | ⭐⭐⭐⭐⭐ (ง่ายมาก) |

---

### โครงสร้างตาราง (Table Schema) บน Supabase/PostgreSQL

หากใช้ Supabase สามารถนำคำสั่ง SQL นี้ไปรันในช่อง SQL Editor เพื่อสร้างตารางได้ทันที:

```sql
CREATE TABLE flood_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ DEFAULT now(),
    source_platform TEXT,            -- 'Facebook', 'TikTok'
    source_url TEXT UNIQUE,          -- ป้องกันโพสต์ซ้ำด้วย UNIQUE
    province TEXT,                   -- เช่น 'ปราจีนบุรี'
    district TEXT,                   -- เช่น 'กบินทร์บุรี'
    subdistrict TEXT,                -- เช่น 'กบินทร์'
    village_or_landmark TEXT,        -- จุดสังเกต/หมู่บ้าน
    urgency TEXT,                    -- 'CRITICAL', 'HIGH', 'MEDIUM'
    needs TEXT[],                    -- รายการสิ่งที่ต้องการ ['ข้าว', 'เรือ']
    contact TEXT,                    -- เบอร์โทรศัพท์
    summary TEXT,                    -- สรุปเหตุการณ์
    status TEXT DEFAULT 'OPEN',      -- 'OPEN', 'IN_PROGRESS', 'RESOLVED'
    assigned_team TEXT               -- ทีมกู้ภัยที่รับเคสไป
);

-- สร้าง Index เพื่อให้กู้ภัยค้นหาตามพื้นที่ได้รวดเร็ว
CREATE INDEX idx_flood_location ON flood_reports (province, district, subdistrict, status);
```

---

### ตัวอย่างโค้ด Python บันทึกลง Supabase

ติดตั้งไลบรารี:
```bash
pip install supabase
```

```python
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")       # ดูได้จากหน้า Settings ใน Supabase
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # หรือ Anon Key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def save_report_to_db(report_data: dict):
    """บันทึกเคสผู้ประสบภัยลงฐานข้อมูลกลาง"""
    try:
        # ใช้ upsert เพื่อข้ามอัตโนมัติหาก source_url ซ้ำ
        response = supabase.table("flood_reports").upsert(
            report_data, 
            on_conflict="source_url"
        ).execute()
        print(">> บันทึกข้อมูลลงฐานข้อมูลสำเร็จ")
        return response.data
    except Exception as e:
        print(f">> บันทึกลงฐานข้อมูลล้มเหลว: {e}")
        return None
```

<FollowUp label="ต้องการดูวิธีตั้งค่า Supabase แบบทีละสเต็ป พร้อมวิธีนำ Key มาใส่ในโค้ดไหม?" query="ขอวิธีสมัครและตั้งค่า Supabase สำหรับโปรเจกต์ flood-distress-detector พร้อมวิธีดู API URL และ Key"/>

---

# you asked

message time: 2026-09-30 16:30:41

อยากจะทำแค่เป็น template แค่ใส่ suberbase api อย่างเดียวไมไ่ด้หรอ

---

# gemini response

**ได้แน่นอนครับ และเป็นวิธีที่ฉลาดที่สุดในการทำ Template แจกจ่ายเลย** 

เพราะถ้าเราออกแบบให้คนรันกรอกแค่ **`SUPABASE_URL`** กับ **`SUPABASE_KEY`** เพียงอย่างเดียว:
1. **คนรันไม่ต้องเสียเงินสักบาท:** ไม่ต้องสมัคร OpenAI ไม่ต้องใช้ Whisper หรือ Apify ในเครื่องตัวเอง
2. **เครื่องสเปกต่ำก็รันได้:** แค่ดึงข้อมูลดิบแล้วยิงเข้า Supabase ตรงๆ
3. **คนทั่วไปใช้งานง่ายมาก:** โคลนโปรเจกต์มา ใส่ 2 ค่านี้แล้วกด Enter รันได้ทันที

---

### ระบบจะทำงานอย่างไรถ้าใส่แค่ Supabase API?

เราจะเปลี่ยนภาระงานหนักๆ ทั้งหมดไปไว้บน Cloud ของคุณ (Central Project) ผ่าน **Supabase Edge Functions / Database Webhook**:

```text
[เครื่องอาสาที่รัน Template]
       │
       │ (ใส่แค่ SUPABASE_URL / KEY)
       │ ส่งเฉพาะข้อมูลดิบ: URL วิดีโอ + Caption + พิกัดคร่าวๆ
       ▼
[Supabase Database (ของคุณ)]
       │
       │ Trigger ทำงานอัตโนมัติ (Webhook / Edge Function)
       ▼
[Serverless ทำ AI ถอดเสียง Whisper + สกัด DOPA พิกัด + ยิง Telegram]
```

* **คนรัน Template:** หน้าที่เหลือแค่เป็น **"Scraper Node"** ส่งข้อมูลเข้ามาเก็บในตารางกลาง
* **ระบบของคุณ (เจ้าของ Template):** ตั้งค่าหลังบ้านครั้งเดียวให้คอยประมวลผลข้อความและส่งแจ้งเตือน

---

### โค้ดตัวอย่าง Template ที่ผู้ใช้กรอกแค่ Supabase

ไฟล์คอนฟิก `.env` ของผู้ใช้งานจะสั้นเหลือแค่นี้:

```env
SUPABASE_URL=https://xyzcompany.supabase.co
SUPABASE_KEY=eyJhbGciOi...
TARGET_PAGE=https://www.facebook.com/example_rescue_page
```

#### `main.py` (ฝั่งผู้ใช้งานรัน)
```python
import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client
# ไลบรารีดึงข้อมูลง่ายๆ หรือ scraper ในเครื่อง
import yt_dlp

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TARGET_PAGE = os.getenv("TARGET_PAGE")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("กรุณากรอก SUPABASE_URL และ SUPABASE_KEY ในไฟล์ .env")

# เชื่อมต่อ Supabase ตรงๆ
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def collect_and_push(video_url: str, caption: str, platform: str):
    """ส่งข้อมูลดิบเข้าตารางกลาง ให้หลังบ้านไปจัดการต่อเอง"""
    payload = {
        "source_url": video_url,
        "caption": caption,
        "platform": platform,
        "status": "PENDING_PROCESS"  # รอระบบ AI หลังบ้านมาดึงไปวิเคราะห์
    }
    
    try:
        # ใช้ upsert เพื่อไม่ให้เก็บ URL ซ้ำ
        res = supabase.table("raw_flood_feeds").upsert(payload, on_conflict="source_url").execute()
        print(f"บันทึกข้อมูลสำเร็จ: {video_url}")
    except Exception as e:
        print(f"ส่งข้อมูลไม่สำเร็จ: {e}")

# ตัวอย่างการทำงาน
if __name__ == "__main__":
    print("เริ่มระบบส่งข้อมูลเข้าศูนย์กลาง...")
    # โค้ดดึง feed วนลูปส่งข้อมูล...
```

---

### ข้อดีของการออกแบบสถาปัตยกรรมแบบนี้

* **การคุมงบประมาณ:** คุณเป็นคนคุม OpenAI Key อยู่ที่ส่วนกลางที่เดียว ไม่ต้องกังวลว่าคีย์จะหลุดหรือคนเอาไปใช้ผิดวัตถุประสงค์
* **อัปเดตระบบ AI ได้ตลอดเวลา:** วันนี้ใช้ Whisper พรุ่งนี้อยากเปลี่ยนเป็น Gemini Flash หรืออยากแก้ Prompt จัดการตำบล/อำเภอ คุณแก้ที่หลังบ้านได้เลย คนที่รัน Template ในพื้นที่ไม่ต้องอัปเดตโค้ดใหม่
* **ความง่ายระดับสูงสุด:** ผู้ช่วยงานในพื้นที่ (เช่น น้องๆ นักศึกษา หรือกู้ภัยที่เขียนโค้ดไม่เก่ง) แค่ก๊อบปี้ Key ที่คุณแจกให้ไปแปะ ก็เปิดระบบช่วยดึงข้อมูลเข้าสู่ศูนย์กลางได้ทันทีครับ

---

# you asked

message time: 2026-09-30 16:31:31

ถ้าจะทำ เราจะต้องมี doc และ diagram หรือ flowchart เพื่อความเข้าใจง่ายๆด้วย

---

# gemini response

เพื่อให้คนที่สนใจเข้ามาร่วมรัน Node หรือทีมกู้ภัยที่นำข้อมูลไปใช้เข้าใจตรงกันใน 1 นาที ควรแบ่ง Document และ Flowchart ออกเป็น 3 ส่วนหลัก: ภาพรวมการทำงาน, สถาปัตยกรรมระบบ, และคู่มือเริ่มรัน (Quickstart Guide)

---

## 1. Flowchart การไหลของข้อมูล (End-to-End Pipeline)

```text
[ชาวบ้านโพสต์ TikTok / FB]
           │
           ▼
[อาสาสมัครรัน Node ประจำพื้นที่] ── (ใส่แค่ SUPABASE_URL / KEY)
           │
           │ ส่งเฉพาะข้อมูลดิบ (URL + Caption)
           ▼
┌────────────────────────────────────────────────────────┐
│  ฐานข้อมูลกลาง (Supabase Hub)                            │
│                                                        │
│  [ตาราง: raw_flood_feeds]                              │
│       │ (Trigger: มีข้อมูลใหม่เข้ามา)                   │
│       ▼                                                │
│  [Edge Function / Worker หลังบ้าน]                     │
│       ├─ 1. yt-dlp ดึงเสียงเฉพาะแทร็ก .mp3             │
│       ├─ 2. Whisper STT ถอดเสียงภาษาไทย                 │
│       ├─ 3. LLM ทำ Normalization พิกัด (DOPA)          │
│       └─ 4. ตรวจจับและอัปเดตข้อมูลซ้ำ (Deduplication)   │
│       │                                                │
│       ▼                                                │
│  [ตาราง: verified_distress_cases]                      │
└────────────────────────────────────────────────────────┘
           │
           ├──────────────────────────────┐
           ▼                              ▼
[Telegram Bot แจ้งเตือนฉุกเฉิน]   [เว็บ Dashboard / แผนที่กู้ภัย]
• แยกห้องตามจังหวัด/เขต            • ค้นหาตามตำบล/อำเภอ
• แนบเบอร์โทร + รายการของที่ต้องการ • กู้ภัยกดปุ่ม "รับเคสนี้แล้ว"
```

---

## 2. โครงสร้าง Database Schema (สำหรับใส่ใน Doc)

ระบบใช้ 2 ตารางหลักเพื่อแยกงานระหว่าง **"คนส่งข้อมูลดิบ"** กับ **"ข้อมูลพร้อมใช้งานของกู้ภัย"**:

```text
+-----------------------+           +-----------------------------+
|    raw_flood_feeds    |           |   verified_distress_cases   |
+-----------------------+           +-----------------------------+
| id (UUID)             |           | id (UUID)                   |
| created_at            |           | created_at                  |
| source_url (UNIQUE)   |──(ประมวล)─>| source_url                  |
| caption               |   ผลต่อ    | province (เช่น ปราจีนบุรี)  |
| platform (FB/TikTok)  |           | district (เช่น กบินทร์บุรี) |
| status (PENDING/DONE) |           | subdistrict (เช่น กบินทร์)  |
+-----------------------+           | landmark_detail             |
                                    | urgency (CRITICAL/HIGH/MED) |
                                    | needs (ARRAY: ข้าว, เรือ)   |
                                    | contact_phone               |
                                    | case_status (OPEN/RESOLVED) |
                                    +-----------------------------+
```

---

## 3. เอกสาร Quickstart สำหรับอาสาสมัคร (README.md Template)

สามารถนำส่วนนี้ไปใช้เป็นหน้าแรกของ GitHub Repository ได้ทันที:

```markdown
# 🌊 Open Flood Node: ตัวกระจายฟีดช่วยเหลือผู้ประสบภัย

เครื่องมือน้ำหนักเบาสำหรับให้อาสาสมัครในแต่ละพื้นที่รันเพื่อรวบรวมฟีดน้ำท่วมจาก TikTok/Facebook 
ส่งเข้าฐานข้อมูลกลางโดยไม่ต้องตั้งค่า Server หรือจ่ายค่า API ใดๆ

---

### 📋 สิ่งที่ต้องเตรียม
1. คอมพิวเตอร์หรือ Server ที่ลง Python 3.10+ (หรือ Docker)
2. กุญแจ `SUPABASE_URL` และ `SUPABASE_KEY` (รับจากผู้ดูแลระบบกลาง)

---

### ⚙️ ขั้นตอนการติดตั้ง (3 ขั้นตอนเสร็จ)

1. **โคลนโปรเจกต์:**
   git clone https://github.com/your-username/open-flood-node.git
   cd open-flood-node

2. **กำหนดค่าในไฟล์ .env:**
   cp .env.example .env

   เปิดไฟล์ `.env` แล้วแก้ไขเฉพาะ 3 บรรทัดนี้:
   SUPABASE_URL=https://flood-center.supabase.co
   SUPABASE_KEY=eyJhbGciOi...
   TARGET_PAGE_OR_TAG=https://www.facebook.com/groups/local_news

3. **สั่งรัน:**
   # แบบใช้ Python ปกติ
   pip install -r requirements.txt
   python main.py

   # หรือรันผ่าน Docker
   docker compose up -d

---

### 🛡️ ความเป็นส่วนตัวและความปลอดภัย
- Node นี้รวบรวมเฉพาะโพสต์/คลิปที่เป็น **สาธารณะ (Public)** เท่านั้น
- ไม่มีการดึงข้อมูลส่วนตัวของเครื่องที่รัน ระบบส่งเฉพาะ URL และข้อความแคปชันไปยังศูนย์กลาง
```

---

## 4. แผนภาพลำดับงานของกู้ภัยหน้างาน (Rescue Dispatch Sequence)

```text
กู้ภัยประจำพื้นที่            ระบบกลาง / Telegram Bot
       │                                │
       │─── 1. พิมพ์ /find กบินทร์ ───────>│
       │                                │ (Query: province='ปราจีนบุรี'
       │                                │         district='กบินทร์บุรี'
       │                                │         status='OPEN')
       │<── 2. ส่งลิสต์เคสด่วน 5 เคส ─────│
       │       พร้อมเบอร์โทรและพิกัดซอย
       │                                │
       │─── 3. กดปุ่ม [รับเคส #104] ────>│
       │                                │ (อัปเดตสถานะเป็น IN_PROGRESS)
       │                                │ (แจ้งเตือนห้องรวม: ทีมสว่างฯ รับเคสแล้ว)
```

การทำเอกสารและแผนภาพแบบนี้แยกชัดเจน จะช่วยให้:
1. **Developer / อาสาสมัคร:** เข้าใจทันทีว่าไม่ต้องเสียเงินค่า Whisper/LLM แค่รัน Node ส่งข้อมูลดิบเข้า Supabase ก็เสร็จ
2. **กู้ภัย / มูลนิธิ:** สบายใจว่ามีระบบกรองตำบล/อำเภอที่แน่นอน ไม่ต้องนั่งอ่านข้อความสแปมหรือข่าวซ้ำในห้องแจ้งเหตุ

<FollowUp label="ต้องการให้เขียนโค้ดตัวอย่างหน้า Web สำหรับกู้ภัยใช้ค้นหาและกดรับเคสด้วยไหม?" query="ขอตัวอย่างหน้าเว็บ HTML/JavaScript แบบ Single Page ที่ต่อตรงกับ Supabase สำหรับให้กู้ภัยค้นหาเคสตามอำเภอและกดเปลี่ยนสถานะ"/>

---

# you asked

message time: 2026-09-30 19:00:13

จะตั้งชื่อ project นี้ว่าอะไรดี

---

# gemini response

การตั้งชื่อโปรเจกต์ Open-source กู้ภัย ควรคำนึงถึง 3 ปัจจัย: **จดจำง่าย เข้าใจหน้าที่ทันที และคนไทย/กู้ภัยเรียกติดปาก** 

นี่คือตัวเลือกชื่อที่แบ่งตามทิศทางและ Mood & Tone ให้เลือกใช้:

---

### กลุ่มที่ 1: ชื่อภาษาไทย สั้น กระชับ กู้ภัยเรียกติดปาก (แนะนำที่สุด)
เหมาะกับการสื่อสารกับจิตอาสา คนในพื้นที่ และทีมกู้ภัยหน้างาน

* **`Phon-Pai` (พ้นภัย / PonPai)** — ตรงตัว ความหมายดี สื่อถึงการช่วยให้ผู้ประสบภัยรอดพ้นจากอันตราย
* **`Siang-Nam` (เสียงน้ำ / SiangNam)** — สื่อถึงฟังก์ชันหลักของระบบโดยตรง คือการ "ฟังเสียงผู้คนจากเหตุการณ์น้ำท่วม"
* **`Chuay-Duan` (ช่วยด่วน / ChuayDuan)** — ตรงไปตรงมา กระตุ้นความเร่งด่วน เหมาะกับระบบ Dispatching เคสฉุกเฉิน
* **`Jai-Nam` (ใจน้ำ / JaiNam)** — สื่อถึงน้ำใจในยามน้ำท่วม และเป็นศูนย์กลางข้อมูล (ใจกลาง)

---

### กลุ่มที่ 2: สากล เท่ สไตล์ Open-source สื่อความหมายชัด (GitHub Friendly)
เหมาะกับการเปิด Public Repo ชวน Dev ทั่วไปมาร่วม Contribute หรือขอสปอนเซอร์ Cloud

* **`FloodVoice`** — แปลตรงตัวว่า "แปลงเสียงวิดีโอจากน้ำท่วมมาเป็นข้อมูล" คนเห็นชื่อปุ๊บรู้ทันทีว่าใช้ AI ฟังเสียง
* **`OpenFloodHub`** — สื่อถึงความเป็น Hub กลางที่ทุกคนสามารถเปิดรัน Node เข้ามารวมข้อมูลกันได้
* **`RescuePulse`** — ชีพจรการกู้ภัย สื่อถึงความ Real-time และการตรวจจับสัญญาณขอความช่วยเหลือ
* **`FloodSignal`** — เน้นมิติการจับสัญญาณขอความช่วยเหลือจาก Social Media

---

### กลุ่มที่ 3: สองพยางค์ คล่องตัว เหมาะทำเป็น CLI หรือ Bot Name
จำง่าย พิมพ์คำสั่งใน Terminal หรือตั้งชื่อใน Telegram สะดวก

* **`NamHub`** (น้ำฮับ) — สั้น ง่าย ผสมคำไทย-อังกฤษ พิมพ์คำสั่ง `namhub start` ได้เท่ๆ
* **`ReliefNode`** — เน้นบทบาทของคนรันว่าคือ Node กระจายความช่วยเหลือ
* **`FlowAid`** — ล้อคำว่า Water Flow กับ First Aid เข้าด้วยกัน

---

### คำแนะนำในการจัดรูปแบบชื่อบน GitHub

หากต้องการความเป็นทางการ แนะนำให้ใช้โครงสร้าง **`[ชื่อหลัก] - [คำอธิบายสั้น]`**:

* **Repo:** `flood-voice` หรือ `ponpai-node`
* **Title ใน README:** 
  > **PhonPai (พ้นภัย) — Crowdsourced AI Distress Signal Pipeline for Flood Relief**
* **Telegram Bot:** `@PhonPaiAlertBot` หรือ `@FloodVoiceBot`

> **ตัวเลือกยอดนิยม:** ถ้าต้องการให้ทั้ง Dev และกู้ภัยเข้าใจตรงกันทันที แนะนำ **`FloodVoice`** (ฝั่งโค้ดอินเตอร์) หรือ **`PhonPai (พ้นภัย)`** (ฝั่งหน้างานไทย) ครับ

---

# you asked

message time: 2026-09-30 19:02:09

![Screenshot 2569-09-30 at 19.01.43.png](images/image-001.png)

ใส่ DSC อะไร และตั้งค่าอะไรบ้าง

---

# gemini response

สำหรับการสร้าง Repository ชื่อ **`FloodVoice-Thai`** แนะนำการตั้งค่าแต่ละช่องดังนี้:

---

### 1. ช่อง Description (คำอธิบายโปรเจกต์)
ก๊อบปี้ข้อความนี้ไปวางได้เลย (มีคีย์เวิร์ดชัดเจนทั้งไทยและอังกฤษ ความยาวพอดีกับโควตา):

> **🌊 Open-source AI pipeline for detecting flood distress signals from Thai social media videos (Whisper + LLM) to dispatch rescue alerts.**

*(หรือแบบภาษาไทยล้วน: `ระบบ Open-source คัดกรองเคสขอความช่วยเหลือเหตุน้ำท่วมจากคลิปวิดีโอ Social Media ด้วย AI เพื่อส่งต่อทีมกู้ภัย`)*

---

### 2. การตั้งค่าในส่วน Configuration

* **Choose visibility:**
  * เลือก **`Public`** (ตามที่เลือกไว้อยู่แล้ว) เพื่อให้คนอื่นและอาสาสมัครเข้ามาร่วมดูโค้ดและรัน Node ช่วยได้

* **Add README:**
  * แนะนำให้เลือก **`Off`** (ปิดไว้ตามภาพ) เพราะเรามีไฟล์ `README.md` เตรียมไว้ในเครื่องแล้ว เดี๋ยวเราจะ Push ขึ้นไปพร้อมชุดโค้ดทั้งหมด (ถ้าเปิด On ไว้ จะเกิดปัญหา Git Conflict ตอน Push ครั้งแรก)

* **Add .gitignore:**
  * ปล่อยเป็น **`No .gitignore`** ไว้ก่อน (เนื่องจากในสคริปต์ zip ที่เราทำ มีไฟล์ `.gitignore` บรรจุอยู่แล้ว)

* **Add license:**
  * กดเลือกเป็น **`MIT License`** (เป็น License มาตรฐานสำหรับ Open-source ที่เปิดให้ทุกคนนำโค้ดไปรัน ดัดแปลง และต่อยอดช่วยเหลือน้ำท่วมได้ฟรีอย่างถูกกฎหมาย)

---

เมื่อกรอกและเลือกตามนี้แล้ว กดปุ่มสีเขียว **`Create repository`** ด้านล่างขวาได้ทันทีครับ

---

# you asked

message time: 2026-09-30 19:05:33

/Plan ตอนนี้ผมใช้บน Computer แล้ว คุณส่ง source code ได้ไหม

---

# gemini response

เนื่องจากระบบแชตไม่สามารถส่งเป็นไฟล์ zip แนบมาให้คลิกดาวน์โหลดโดยตรงได้ แต่บนเครื่องคอมพิวเตอร์ของคุณมีวิธีที่ง่ายและสะอาดที่สุด 2 วิธี:

---

### แผนการทำงาน (Execution Plan)

1. **วิธีที่ 1 (แนะนำ - อัตโนมัติใน 1 คำสั่ง):** รันสคริปต์ Python ใน Terminal เพียงครั้งเดียว เพื่อให้คอมพิวเตอร์ของคุณสร้างโฟลเดอร์โปรเจกต์ `FloodVoice-Thai` พร้อมแตกไฟล์ทั้งหมดออกมาให้ครบ
2. **วิธีที่ 2 (Push ตรงขึ้น GitHub):** รันคำสั่ง Git เพื่อส่งโค้ดเข้า Repository `sufarwee/FloodVoice-Thai` ที่เพิ่งสร้างทันที

---

### ขั้นตอนที่ 1: รันคำสั่งสร้างโค้ดทั้งหมดลงเครื่อง

เปิดโปรแกรม **Terminal** (บน Mac/Linux) หรือ **PowerShell/Command Prompt** (บน Windows) แล้วรันสคริปต์ Python ด้านล่างนี้:

```bash
python3 -c '
import os

files = {
    "requirements.txt": """apify-client>=1.6.0
yt-dlp>=2024.8.6
openai>=1.30.0
supabase>=2.0.0
requests>=2.31.0
pydantic>=2.0.0
python-dotenv>=1.0.0
""",

    ".env.example": """SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-key
TARGET_FACEBOOK_URLS=https://www.facebook.com/example_rescue_page
CHECK_INTERVAL_MINUTES=15
""",

    ".gitignore": """__pycache__/
*.pyc
.env
venv/
*.mp3
*.wav
*.m4a
.DS_Store
""",

    "Dockerfile": """FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
""",

    "docker-compose.yml": """version: "3.8"
services:
  flood-detector:
    build: .
    container_name: flood_voice_node
    restart: unless-stopped
    env_file:
      - .env
""",

    "README.md": """# 🌊 FloodVoice-Thai

ระบบ Open-source คัดกรองเคสขอความช่วยเหลือเหตุน้ำท่วมจากคลิปวิดีโอ Social Media (TikTok / Facebook) ด้วย AI เพื่อส่งต่อทีมกู้ภัย

## 🚀 เริ่มต้นใช้งาน

1. คัดลอก Environment config:
   ```bash
   cp .env.example .env
   ```
2. ใส่ค่า `SUPABASE_URL` และ `SUPABASE_KEY` ที่ได้รับจากศูนย์กลาง
3. รันผ่าน Docker:
   ```bash
   docker compose up -d --build
   ```
   หรือรันด้วย Python:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```
""",

    "main.py": """import os
import time
from dotenv import load_dotenv
from supabase import create_client, Client
from src.fetcher import fetch_target_posts

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
TARGET_URLS = [u.strip() for u in os.getenv("TARGET_FACEBOOK_URLS", "").split(",") if u.strip()]
INTERVAL_MIN = int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("กรุณากำหนดค่า SUPABASE_URL และ SUPABASE_KEY ใน .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
seen_urls = set()

def run_cycle():
    print(f"[{time.strftime("%H:%M:%S")}] ตรวจสอบฟีดข้อมูล...")
    for target in TARGET_URLS:
        posts = fetch_target_posts(target)
        for p in posts:
            if p["url"] in seen_urls:
                continue
            seen_urls.add(p["url"])
            try:
                supabase.table("raw_flood_feeds").upsert({
                    "source_url": p["url"],
                    "caption": p["caption"],
                    "platform": "Facebook",
                    "status": "PENDING"
                }, on_conflict="source_url").execute()
                print(f">> ส่งข้อมูลสำเร็จ: {p[\"url\"]}")
            except Exception as err:
                print(f">> ข้อผิดพลาด DB: {err}")

if __name__ == "__main__":
    print("เริ่มการทำงานของ FloodVoice Node...")
    while True:
        try:
            run_cycle()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(INTERVAL_MIN * 60)
""",

    "src/__init__.py": "",

    "src/fetcher.py": """def fetch_target_posts(target_url: str) -> list[dict]:
    # Placeholder สำหรับดึงโพสต์จาก Scraper หรือ API
    return []
"""
}

os.makedirs("FloodVoice-Thai/src", exist_ok=True)
for path, content in files.items():
    full_path = os.path.join("FloodVoice-Thai", path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("\n สร้างโฟลเดอร์และไฟล์โปรเจกต์ FloodVoice-Thai ครบถ้วนแล้ว!")
'
```

---

### ขั้นตอนที่ 2: Push โค้ดทั้งหมดขึ้น GitHub ทันที

เมื่อรันคำสั่งด้านบนเสร็จแล้ว จะได้โฟลเดอร์ชื่อ `FloodVoice-Thai` ให้รันคำสั่งด้านล่างนี้ต่อเนื่องใน Terminal เพื่อส่งขึ้น GitHub:

```bash
cd FloodVoice-Thai
git init
git add .
git commit -m "feat: initial release of FloodVoice-Thai node template"
git branch -M main
git remote add origin https://github.com/sufarwee/FloodVoice-Thai.git
git push -u origin main
```

*(ระบบจะให้ยืนยันตัวตนของ GitHub ครั้งแรก)* เมื่อคำสั่งทำงานเสร็จ ให้กด Refresh หน้าเว็บ Repository บนเบอร์เกอร์ จะเห็นโค้ดทั้งหมดขึ้นไปอยู่บน GitHub พร้อมใช้งานทันทีครับ

---

# you asked

message time: 2026-09-30 19:06:06

แล้วถ้าใช้งานใน Antigravity ล่ะ จะเข้าถึง chat นี้ยังไง

---

# gemini response

หากคุณใช้งานผ่าน **Antigravity** (หรือแพลตฟอร์ม/เครื่องมือ Agent ในลักษณะนี้) การเข้าถึงหรือเชื่อมต่อประวัติการแชทและการตั้งค่าจากตรงนี้สามารถทำได้ 3 วิธีหลัก:

---

### 1. ล็อกอินด้วยบัญชีเดียวกัน (Account Sync)
* หาก Antigravity รองรับการเชื่อมต่อบัญชีผู้ใช้หรือมีระบบ Sync ข้ามอุปกรณ์ ให้ตรวจสอบว่าได้ลงชื่อเข้าใช้ด้วย **บัญชี Google/ผู้ใช้งานเดียวกัน** ระบบจะดึงประวัติการสนทนา (Chat History) ล่าสุดมาแสดงผลให้โดยอัตโนมัติ

---

### 2. นำเข้าเป็น System Context / Memory ใน Workspace (แนะนำที่สุด)
หาก Antigravity เป็นระบบแยกที่ไม่มีประวัติแชตข้ามมา คุณสามารถตั้งค่า Workspace ใหม่ใน Antigravity โดยนำบริบทของโปรเจกต์นี้ไปใส่เป็น **System Prompt** หรือ **Project Context** ได้ทันที:

```text
Project: FloodVoice-Thai (Open-source flood distress detection)
Repository: https://github.com/sufarwee/FloodVoice-Thai
Current Architecture: 
- Distributed Node collects raw feeds (Facebook/TikTok)
- Central Database: Supabase (raw_flood_feeds -> verified_distress_cases)
- Processing Pipeline: Audio extraction (yt-dlp) -> STT (Whisper) -> DOPA Location Normalizer (LLM) -> Telegram Dispatcher
- Tech Stack: Python 3.11, Docker, Pydantic, Supabase, OpenAI
```
การแปะสรุปนี้ลงในโปรเจกต์ของ Antigravity จะทำให้ AI ในระบบนั้นเข้าใจบริบทต่อจากจุดนี้ได้ทันทีโดยไม่ต้องเริ่มต้นอธิบายใหม่

---

### 3. เชื่อมต่อผ่าน Git Repository โดยตรง
เนื่องจากเราสร้าง Repository `FloodVoice-Thai` ไว้บน GitHub แล้ว คุณสามารถสั่งให้ Antigravity:
* **Clone Repository:** ดึงโค้ดจาก `[https://github.com/sufarwee/FloodVoice-Thai](https://github.com/sufarwee/FloodVoice-Thai)` เข้าสู่ Workspace
* โค้ดทั้งหมด, ไฟล์ `README.md`, และโครงสร้างสถาปัตยกรรมจะกลายเป็นฐานข้อมูลหลักที่ Antigravity ใช้อ่านและพัฒนาต่อได้โดยตรงทันทีครับ