import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from config import GEMINI_API_KEY, OPENAI_API_KEY, DEFAULT_AI_PROVIDER
from .schemas import DistressReport, NormalizedLocation, UrgencyLevel, WaterLevelCode

ANALYZER_SYSTEM_PROMPT = """ระบบวิเคราะห์และคัดกรองข้อมูลภัยพิบัติน้ำท่วมสำหรับศูนย์ประสานงานกู้ภัย (Flood Emergency Data Analyst)

หน้าที่ของระบบ:
วิเคราะห์ข้อความ แคปชัน เสียงพูดที่ถอดได้ และภาพจากคลิปวิดีโอ/Live เพื่อสกัดข้อมูลผู้ประสบภัยอย่างแม่นยำ

กฎเกณฑ์สำคัญในการวิเคราะห์:
1. การระบุระดับความสูงของน้ำ (Water Level):
   - ระดับ 1 (LEVEL_1_LOW): ท่วมขังระดับตาตุ่ม, ข้อเท้า, หน้าแข้ง, ถนนมีน้ำเอ่อ
   - ระดับ 2 (LEVEL_2_MEDIUM): ท่วมระดับหัวเข่า, ใต้ถุนบ้าน, ครึ่งล้อรถยนต์
   - ระดับ 3 (LEVEL_3_HIGH): ท่วมระดับเอว, มิดล้อรถ, ไฟฟ้าเริ่มตัด, เดินลำบาก
   - ระดับ 4 (LEVEL_4_CRITICAL): ท่วมระดับอก ถึง ระดับคอ, กระแสน้ำเชี่ยว, สัญจรได้เฉพาะเรือท้องแบน/เจ็ตสกี
   - ระดับ 5 (LEVEL_5_EMERGENCY): ท่วมมิดหัว, มิดชั้น 1 ต้องปีนขึ้นหลังคา, มีคนติดค้าง/ผู้ป่วยติดเตียง/เด็กอ่อนในภาวะวิกฤต

2. การจำแนกความต้องการเฉพาะเจาะจง (Needs):
   - ตรวจจับคำว่า: ยาประจำตัว (เบาหวาน, ความดัน, ฟอกไต), นมผง/แพมเพิสเด็ก, ข้าวกล่อง/น้ำดื่ม, เรืออพยพ, เครื่องสูบน้ำ, ไฟฉาย/เทียน

3. โครงสร้างพิกัดตามมาตรฐานกรมการปกครอง (DOPA):
   - ถ้าเป็น กรุงเทพมหานคร: province="กรุงเทพมหานคร", district="เขต..." (ตัดคำว่า เขต ออก), subdistrict="แขวง..." (ตัดคำว่า แขวง ออก)
   - ต่างจังหวัด: province="จังหวัด...", district="อำเภอ...", subdistrict="ตำบล..." (ตัดคำนำหน้าออก)
   - ขยายชื่อย่อเสมอ เช่น "โคราช" -> "นครราชสีมา", "แปดริ้ว" -> "ฉะเชิงเทรา", "แม่สาย" -> อำเภอ "แม่สาย" จังหวัด "เชียงราย"
   - รายละเอียดหมู่บ้าน ซอย ชุมชน ให้ใส่ใน village_or_community หรือ landmark_detail

4. ระดับความเร่งด่วน (Urgency Level):
   - CRITICAL: น้ำระดับอก/คอ/หลังคา หรือมีผู้ป่วยติดเตียง/คนชรา/เด็กอ่อน หรือขาดอาหารยาเกิน 24 ชม.
   - HIGH: น้ำระดับเอว ต้องการเรืออพยพ หรือเริ่มขาดน้ำและอาหาร
   - MEDIUM: น้ำระดับเข่า ท่วมเข้าบ้าน ต้องการกระสอบทรายหรือเสบียง
   - LOW: น้ำท่วมขังทั่วไป รถวิ่งลำบาก หรือรายงานข่าวสถานการณ์
"""

class MultimodalAnalyzer:
    def __init__(self, provider: Optional[str] = None):
        self.provider = provider or DEFAULT_AI_PROVIDER
        self.gemini_client = None
        self.openai_client = None
        self._init_clients()

    def _init_clients(self):
        # 1. เชื่อมต่อ Gemini SDK เมื่อมี API Key
        if GEMINI_API_KEY:
            try:
                from google import genai
                self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception:
                pass

        # 2. เชื่อมต่อ OpenAI SDK เมื่อมี API Key
        if OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
            except Exception:
                pass


    def analyze(
        self,
        text_content: str,
        audio_path: Optional[str] = None,
        image_paths: Optional[List[str]] = None
    ) -> DistressReport:
        """
        วิเคราะห์ข้อมูลมัลติโมดอล (ข้อความ + ไฟล์เสียง + รูปภาพ)
        """
        # พยายามรันด้วย Gemini ก่อนถ้ามี Client
        if self.gemini_client and (self.provider == "gemini" or not self.openai_client):
            try:
                return self._analyze_with_gemini(text_content, audio_path, image_paths)
            except Exception as e:
                print(f"Gemini analysis error: {e}, attempting fallback...")

        # ถ้า Gemini ใช้ไม่ได้ ให้ลอง OpenAI
        if self.openai_client:
            try:
                return self._analyze_with_openai(text_content, audio_path)
            except Exception as e:
                print(f"OpenAI analysis error: {e}")

        # Fallback แบบ Rule-based สำหรับการทดสอบในเครื่องโดยยังไม่มี API Key
        return self._heuristic_fallback(text_content)

    def _analyze_with_gemini(
        self,
        text_content: str,
        audio_path: Optional[str] = None,
        image_paths: Optional[List[str]] = None
    ) -> DistressReport:
        from google.genai import types

        contents = [ANALYZER_SYSTEM_PROMPT, f"ข้อความและบริบทเหตุการณ์:\n{text_content}"]

        # แนบไฟล์เสียงถ้ามี
        if audio_path and os.path.exists(audio_path):
            audio_bytes = Path(audio_path).read_bytes()
            mime = "audio/mp3" if audio_path.endswith(".mp3") else "audio/wav"
            contents.append(types.Part.from_bytes(data=audio_bytes, mime_type=mime))

        # แนบรูปภาพถ้ามี
        if image_paths:
            for img_path in image_paths[:3]: # สูงสุด 3 ภาพ
                if os.path.exists(img_path):
                    img_bytes = Path(img_path).read_bytes()
                    contents.append(types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"))

        # ใช้ gemini-2.5-flash หรือ gemini-1.5-flash
        model_name = "gemini-2.5-flash"
        response = self.gemini_client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=DistressReport,
                temperature=0.1
            ),
        )
        data = json.loads(response.text)
        return DistressReport(**data)

    def transcribe_audio(self, audio_path: str) -> str:
        """ถอดเสียงพูดภาษาไทย รองรับทั้ง Local Mac Whisper (ออฟไลน์) และ OpenAI Whisper API"""
        if not audio_path or not os.path.exists(audio_path):
            return ""

        from config import WHISPER_MODE, LOCAL_WHISPER_MODEL

        # 1. ถ้าเลือกโหมด Local (Mac Whisper) ให้รันในเครื่องฟรี 100%
        if WHISPER_MODE == "local":
            try:
                from .local_whisper import transcribe_local_mac
                print(f"-> กำลังถอดเสียงด้วย Local Mac Whisper (โมเดล: {LOCAL_WHISPER_MODEL})...")
                text = transcribe_local_mac(audio_path, model_size=LOCAL_WHISPER_MODEL)
                if text:
                    return text
            except Exception as e:
                print(f"Local Whisper note: {e}, falling back to API if available...")

        # 2. ถอดเสียงผ่าน OpenAI Whisper API (ถ้ามี Client)
        if self.openai_client:
            try:
                print("-> กำลังถอดเสียงผ่าน OpenAI Whisper API (whisper-1)...")
                with open(audio_path, "rb") as f:
                    tr = self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                        language="th"
                    )
                    return tr.text or ""
            except Exception as e:
                print(f"OpenAI Whisper API error: {e}")

        return ""

    def _analyze_with_openai(
        self,
        text_content: str,
        audio_path: Optional[str] = None
    ) -> DistressReport:
        combined_text = text_content

        # ถอดเสียงด้วย Whisper (รองรับทั้ง Local และ API)
        if audio_path and os.path.exists(audio_path):
            transcript = self.transcribe_audio(audio_path)
            if transcript:
                combined_text += f"\n[เสียงพูดในวิดีโอ]: {transcript}"

        completion = self.openai_client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": ANALYZER_SYSTEM_PROMPT},
                {"role": "user", "content": combined_text},
            ],
            response_format=DistressReport,
        )
        return completion.choices[0].message.parsed

    def _heuristic_fallback(self, text: str) -> DistressReport:
        """
        ระบบ Rule-based กรองเบื้องต้นสำหรับทดสอบกรณีไม่มี API Keys
        """
        text_lower = text.lower()
        is_distress = any(kw in text for kw in ["น้ำท่วม", "ช่วยด้วย", "ติดน้ำ", "ต้องการ", "จม", "เรือ"])
        
        # ตรวจจับระดับน้ำ
        water_level = "ไม่ระบุ"
        water_code = WaterLevelCode.LEVEL_UNKNOWN
        if any(w in text for w in ["มิดหลังคา", "ชั้น 2", "มิดหัว", "หลังคา"]):
            water_level = "มิดหลังคา/ชั้น 2"
            water_code = WaterLevelCode.LEVEL_5_EMERGENCY
        elif any(w in text for w in ["ระดับอก", "ถึงอก", "มิดอก", "ระดับคอ", "ถึงคอ", "น้ำเชี่ยว"]):
            water_level = "ระดับอก/คอ"
            water_code = WaterLevelCode.LEVEL_4_CRITICAL
        elif any(w in text for w in ["ระดับเอว", "ถึงเอว", "มิดล้อ"]):
            water_level = "ระดับเอว"
            water_code = WaterLevelCode.LEVEL_3_HIGH
        elif any(w in text for w in ["หัวเข่า", "ถึงเข่า", "ระดับเข่า"]):
            water_level = "ระดับหัวเข่า"
            water_code = WaterLevelCode.LEVEL_2_MEDIUM
        elif any(w in text for w in ["ตาตุ่ม", "ข้อเท้า", "ถึงตาตุ่ม"]):
            water_level = "ระดับตาตุ่ม"
            water_code = WaterLevelCode.LEVEL_1_LOW


        # ตรวจจับความด่วน
        if water_code in (WaterLevelCode.LEVEL_5_EMERGENCY, WaterLevelCode.LEVEL_4_CRITICAL) or "ติดเตียง" in text:
            urgency = UrgencyLevel.CRITICAL
        elif water_code == WaterLevelCode.LEVEL_3_HIGH or "เรือ" in text:
            urgency = UrgencyLevel.HIGH
        elif is_distress:
            urgency = UrgencyLevel.MEDIUM
        else:
            urgency = UrgencyLevel.LOW

        # ตรวจจับความต้องการ
        needs = []
        if "เรือ" in text: needs.append("เรือพาย/เรือท้องแบน")
        if "อาหาร" in text or "ข้าว" in text: needs.append("อาหารแห้ง/ข้าวกล่อง")
        if "น้ำ" in text: needs.append("น้ำดื่ม")
        if "ยา" in text: needs.append("ยารักษาโรค/ยาประจำตัว")
        if "นม" in text or "เด็ก" in text: needs.append("นมผงเด็ก/ของใช้เด็กอ่อน")
        if "ติดเตียง" in text or "คนแก่" in text: needs.append("อพยพผู้ป่วยติดเตียง/คนชรา")

        # ตรวจจับจังหวัดง่ายๆ
        province = "ไม่ระบุ"
        for p in ["ปราจีนบุรี", "เชียงราย", "พะเยา", "น่าน", "แพร่", "สุโขทัย", "อยุธยา", "กรุงเทพมหานคร"]:
            if p in text or (p == "กรุงเทพมหานคร" and ("กทม" in text or "กรุงเทพ" in text)):
                province = p
                break

        return DistressReport(
            is_distress=is_distress,
            urgency_level=urgency,
            water_level=water_level,
            water_level_code=water_code,
            location=NormalizedLocation(
                is_bangkok=(province == "กรุงเทพมหานคร"),
                province=province if province != "ไม่ระบุ" else None,
                district=None,
                subdistrict=None,
                landmark_detail=text[:60]
            ),
            needs=needs,
            headcount=None,
            contact_info=None,
            summary=f"รายงานเหตุน้ำท่วม: {text[:80]}..."
        )
