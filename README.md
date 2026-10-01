# 🌊 FloodVoice (เสียงน้ำท่วม)
> **ระบบเฝ้าระวังและคัดกรองสัญญาณขอความช่วยเหลือเหตุน้ำท่วมจาก Social Media**  
> *Open-Source Disaster Response Pipeline for Detecting Thai Flood Distress Signals*

[![Version: 1.2.0](https://img.shields.io/badge/version-1.2.0-blue.svg)](https://github.com/sufarwee/FloodVoice-Thai/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-green.svg)](https://www.docker.com/)

**FloodVoice** คือเครื่องมือโอเพนซอร์สที่สร้างขึ้นเพื่อสนับสนุนการทำงานของ **ทีมกู้ภัย, ศูนย์สั่งการภัยพิบัติ, องค์กรปกครองส่วนท้องถิ่น และอาสาสมัคร** ในการค้นหาเสียงขอความช่วยเหลือของประชาชนที่โพสต์ผ่าน Social Media (Facebook, Instagram, TikTok, YouTube และ X/Twitter) ทั้งในรูปแบบข้อความ, คลิปสั้น Reels/Shorts และ **Live ถ่ายทอดสด**

ระบบจะถอดเสียงพูดภาษาไทย สกัดระดับความสูงของน้ำ (ตาตุ่ม/เข่า/เอว/อก/คอ/มิดหลังคา) ระบุความต้องการฉุกเฉิน (ยาประจำตัว/นมเด็ก/เรือ/ผู้ป่วยติดเตียง) และจัดพิกัดตามมาตรฐานกรมการปกครอง (DOPA) เพื่อส่งต่อข้อมูลไปยัง **Google Sheets**, **Obsidian Markdown** และ **Telegram** ได้ทันท่วงที

---

## 🗺️ แผนผังการทำงาน (System Architecture)

```mermaid
flowchart TD
    subgraph Sources["1. แหล่งข้อมูล Social Media"]
        FB["Facebook / IG (Posts & Reels)"]
        TT["TikTok (Videos & Hashtags)"]
        YT["YouTube (Live Stream & Videos)"]
        X["X (Twitter)"]
    end

    subgraph Ingestion["2. ดึงข้อมูลและตัดเสียง"]
        YTDL["yt-dlp Engine\n(สกัดเสียง .mp3 + เฟรมภาพ โดยไม่โหลดไฟล์วิดีโอเต็ม)"]
    end

    subgraph Processing["3. ประมวลผลและจำแนกข้อมูล"]
        STT["ถอดเสียงพูดภาษาไทย (Thai Speech-to-Text)"]
        WL["จัดระดับความสูงของน้ำ (ตาตุ่ม/เข่า/เอว/อก/คอ/หลังคา)"]
        Needs["คัดกรองสิ่งของจำเป็น (ยา/นมเด็ก/เรือ/ผู้ป่วย)"]
        DOPA["ปรับพิกัดตามมาตรฐานกรมการปกครอง (DOPA)"]
    end

    subgraph Out["4. ปลายทางสำหรับทีมกู้ภัย"]
        GS["Google Sheets\n(กู้ภัยเปิดดูบนมือถือ + Dropdown รับงาน)"]
        OB["Obsidian Markdown\n(การ์ดเหตุการณ์ + ตารางสรุปรายวัน)"]
        TG["Telegram Alert\n(ยิงแจ้งเตือนเข้าห้องกู้ภัยประจำพื้นที่)"]
    end

    Sources --> YTDL
    YTDL --> STT
    STT --> WL
    WL --> Needs
    Needs --> DOPA
    DOPA --> GS
    DOPA --> OB
    DOPA --> TG
```

---

## 🔑 คู่มือตั้งค่า API Keys (ต้องเปลี่ยนตรงไหนบ้าง?)

คัดลอกไฟล์ `.env.example` ไปเป็น `.env` ก่อนเริ่มใช้งาน:
```bash
cp .env.example .env
```

| ตัวแปรในไฟล์ `.env` | หน้าที่การทำงาน | แหล่งที่มา / วิธีขอรับ |
| :--- | :--- | :--- |
| **`GEMINI_API_KEY`**<br>`⭐ แนะนำเป็นหลัก (ฟรี)` | วิเคราะห์ข้อความ แคปชัน เสียงพูดภาษาไทย และจัดระดับน้ำ | ขอฟรีได้ที่ [Google AI Studio](https://aistudio.google.com/) *(ไม่ต้องใช้บัตรเครดิต)* |
| **`WHISPER_MODE`**<br>`("api" หรือ "local")` | เลือกระบบถอดเสียง: `local` (Mac Whisper ฟรีในเครื่อง) หรือ `api` (OpenAI Whisper) | กำหนดใน `.env` (ค่าเริ่มต้น: `api`) |
| **`LOCAL_WHISPER_MODEL`**<br>`(ค่าเริ่มต้น: "base")` | ขนาดโมเดล Local Mac Whisper: `tiny`, `base`, `small`, `medium` | โหลดอัตโนมัติเมื่อตั้งโหมด `local` |
| **`OPENAI_API_KEY`**<br>`(เมื่อใช้ Whisper API)` | ถอดเสียงด้วย OpenAI Whisper-1 และโมเดล GPT-4o-mini | ขอรับได้ที่ [OpenAI API Keys](https://platform.openai.com/api-keys) |
| **`DEFAULT_AI_PROVIDER`**<br>`(ค่าเริ่มต้น: gemini)` | เลือกว่าจะใช้ระบบวิเคราะห์ตัวใดเป็นหลัก (`gemini` หรือ `openai`) | กำหนดในไฟล์ `.env` ได้เลย |
| **`GOOGLE_SHEET_ID`**<br>`(แนะนำสำหรับกู้ภัย)` | รหัส Spreadsheet สำหรับส่งข้อมูลอัปเดตลงตาราง Real-time | ดูรหัสจาก URL ของ Google Sheet ที่สร้างไว้ |
| **`GOOGLE_SERVICE_ACCOUNT_FILE`**<br>`(เมื่อใช้ Google Sheets)` | ไฟล์ Key สิทธิ์การเข้าถึง (`service_account.json`) | สร้าง Service Account ใน Google Cloud Console แล้วแชร์ Sheet ให้บอท |
| **`TELEGRAM_BOT_TOKEN`**<br>`(ทางเลือกแจ้งเตือน)` | โทเคนบอทสำหรับยิงแจ้งเตือนเคสฉุกเฉิน | คุยกับ [@BotFather](https://t.me/BotFather) ใน Telegram พิมพ์ `/newbot` |
| **`TELEGRAM_CHAT_ID`**<br>`(ทางเลือกแจ้งเตือน)` | ID ห้องแชตหรือกลุ่มกู้ภัยที่ต้องการรับแจ้งเตือน | ดึงบอทเข้ากลุ่ม แล้วเช็ก ID ผ่านคำสั่งบอท |
| **`YOUTUBE_API_KEY`**<br>`(ทางเลือก)` | ค้นหา Live Stream และคลิปน้ำท่วมบน YouTube | เปิดใช้ YouTube Data API v3 ฟรี *(หากไม่ใส่ ระบบจะค้นหาผ่าน yt-dlp ให้อัตโนมัติ)* |
| **`APIFY_TOKEN`**<br>`(สำหรับ FB, IG, TikTok, X)` | ดึงโพสต์และฟีดจาก Social Media 4 แพลตฟอร์ม | รับโทเคนฟรีได้จาก [Apify.com](https://apify.com/) *(มีฟรีเครดิต $5 ทุกเดือน)* |


> [!NOTE]
> **เริ่มใช้งานได้ฟรี 100% ทันที:** เพียงคุณกรอก **`GEMINI_API_KEY`** เพียงตัวเดียว ระบบก็สามารถทำงานได้เต็มรูปแบบทั้งการสแกนและส่งออกผลลัพธ์เป็น Obsidian Markdown ในเครื่อง!  
> เนื่องจากปัจจุบัน Official API บางอย่างจำกัดการเข้าถึงอย่างมากในการทำ Social Listening เช่น TikTok Research API หรือ Meta Graph API (และ CrowdTangle ปิดตัวแล้ว) ทางโปรเจกต์จึงเลือกต่อผ่าน **Apify** มาทดแทนเพื่อให้ใช้งานได้จริงโดยไม่ต้องจ่ายรายปีราคาแพง

---

## 🎙️ ตัวเลือกระบบถอดเสียงภาษาไทย (OpenAI Whisper vs Mac Whisper)

ระบบรองรับระบบถอดเสียงภาษาไทย 2 รูปแบบตามความสะดวกของเครื่องคุณ:

1. **Mac Whisper (Local Offline ในเครื่อง Mac/PC):**
   * **จุดเด่น:** **ฟรี 100% ตลอดชีพ** ไม่เสียค่า API สักบาท และทำงานแบบออฟไลน์ไม่ต้องต่อเน็ต ใช้พลังประมวลผลของ CPU / Apple Silicon (M1/M2/M3/M4) ได้เต็มที่
   * **วิธีเปิดใช้งาน:** 
     1. ติดตั้งไลบรารี: `pip install faster-whisper`
     2. ใน `.env` ตั้งค่า:
        ```env
        WHISPER_MODE=local
        LOCAL_WHISPER_MODEL=base
        ```
2. **OpenAI Whisper API (`whisper-1`):**
   * **จุดเด่น:** ไม่กินสเปกเครื่อง เหมาะสำหรับเครื่องเซิร์ฟเวอร์ขนาดเล็ก หรือรันบน Docker
   * **วิธีเปิดใช้งาน:** ใส่ `OPENAI_API_KEY` ใน `.env` และตั้ง `WHISPER_MODE=api`


---

## 🚀 วิธีการติดตั้งและเริ่มใช้งาน

### วิธีที่ 1: รันบนเครื่องคอมพิวเตอร์ด้วย Python

1. **ดาวน์โหลดโปรเจกต์:**
   ```bash
   git clone https://github.com/sufarwee/FloodVoice-Thai.git
   cd FloodVoice-Thai
   ```

2. **ติดตั้งไลบรารี:**
   *(เครื่องของคุณต้องมี `ffmpeg` สำหรับประมวลผลเสียง เช่น บน Mac รัน `brew install ffmpeg` หรือบน Ubuntu รัน `sudo apt install ffmpeg`)*
   ```bash
   pip install -r requirements.txt
   ```

3. **แก้ไขไฟล์ `.env`:**
   เปิดไฟล์ `.env` แล้วใส่ `GEMINI_API_KEY` ของคุณ

4. **คำสั่งสั่งรัน:**
   ```bash
   # 1. ทดสอบการจำแนกข้อความ
   python3 main.py --test-text "ช่วยด้วยครับ ตอนนี้น้ำท่วมถึงอก ม.3 ต.กบินทร์ อ.กบินทร์บุรี ปราจีนบุรี ติดอยู่ 4 คน ต้องการเรือและอาหารด่วน"

   # 2. ทดสอบดึงเสียงและประมวลผลจากลิงก์วิดีโอ/Live โดยตรง
   python3 main.py --test-url https://www.youtube.com/watch?v=xxxx

   # 3. เริ่มระบบสแกน Social Media อัตโนมัติ (วนลูปทุก 15 นาที)
   python3 main.py --scan
   ```

---

วิธีที่ 2: รันผ่าน Docker (คลิกเดียว ไม่ต้องลงโปรแกรมเพิ่ม)

เหมาะสำหรับเปิดทิ้งไว้บน Server ตลอด 24 ชั่วโมง:
```bash
cp .env.example .env
# กรอก GEMINI_API_KEY ในไฟล์ .env
docker compose up -d --build
```
ระบบจะเปิดบริการเฝ้าระวังอัตโนมัติ โดยไฟล์ผลลัพธ์การ์ด Markdown จะถูกบันทึกไว้ที่โฟลเดอร์ `./obsidian_vault` บนเครื่องของคุณ

---

การปรับแต่งคำค้นหาและจังหวัด (`keywords.json`)

คุณสามารถระบุจังหวัดที่ต้องการเฝ้าระวังหรือคำค้นเฉพาะถิ่นได้ที่ไฟล์ `keywords.json`:

```json
{
  "monitored_provinces": [
    "ปราจีนบุรี",
    "เชียงราย",
    "สุโขทัย",
    "พระนครศรีอยุธยา"
  ],
  "search_keywords": [
    "น้ำท่วม",
    "ติดน้ำท่วม",
    "น้ำเอ่อล้นตลิ่ง",
    "ขอน้ำดื่มอาหาร",
    "ต้องการเรือ"
  ]
}
```

---

 ตัวอย่างผลลัพธ์ใน Google Sheets & Obsidian

| ความเร่งด่วน | ระดับน้ำ | จังหวัด | อำเภอ/เขต | ตำบล/แขวง | สิ่งที่ต้องการด่วน | เบอร์ติดต่อ | ลิงก์ต้นทาง |

| 🔴 CRITICAL | ระดับอก | ปราจีนบุรี | กบินทร์บุรี | กบินทร์ | เรือพาย, นมเด็ก, น้ำดื่ม | 081-xxx-xxxx | [ดูคลิป] |

| 🔴 HIGH | ระดับเอว | เชียงราย | แม่สาย | เวียงพางคำ | ข้าวกล่อง, ยาประจำตัว | 089-xxx-xxxx | [ดู Live สด] |

---

English Summary

**FloodVoice** is an open-source humanitarian tool designed to assist rescue teams and local disaster centers in monitoring and extracting flood distress signals from Thai social media videos, posts, and live streams (Facebook, Instagram, TikTok, and YouTube).

Key Features:
* **Audio & Frame Sampling:** Extracts audio streams and video keyframes via `yt-dlp` without downloading heavy video files.
* **Water Level Severity Classification:** Automatic classification from Ankle (`LEVEL_1`), Knee (`LEVEL_2`), Waist (`LEVEL_3`), Chest/Neck (`LEVEL_4`), to Roof/Submerged (`LEVEL_5`).
* **Specific Relief Needs Extraction:** Identifies critical items (chronic disease medications, infant milk formula, rescue boats, food & water, bedridden patient evacuation).
* **DOPA Administrative Normalization:** Matches informal addresses to official Thai administrative structures (Province, District, Subdistrict).
* **Ready-to-Use Outputs:** Real-time sync to Google Sheets, Obsidian Markdown event cards, and Telegram group dispatching.

---

สัญญาอนุญาต (License)

โปรเจกต์นี้เผยแพร่ภายใต้สัญญาอนุญาต [MIT License](LICENSE) ทุกคนสามารถนำไปใช้งาน แจกจ่าย และพัฒนาต่อยอดเพื่อสาธารณประโยชน์ได้อย่างอิสระ แม้จะเป็นตัวเริ่มต้น ก็หวังว่าจะเป็นประโยชน์นะครับ 
