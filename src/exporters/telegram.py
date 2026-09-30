from typing import Dict, Any, Optional
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class TelegramDispatcher:
    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None
    ):
        self.bot_token = bot_token or TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or TELEGRAM_CHAT_ID

    def send_alert(self, case: Dict[str, Any]) -> bool:
        if not self.bot_token or not self.chat_id:
            return False

        urgency = case.get("urgency_level", "MEDIUM")
        urgency_tag = {
            "CRITICAL": "🚨 [วิกฤตด่วนที่สุด]",
            "HIGH": "🔴 [ด่วนมาก]",
            "MEDIUM": "🟡 [ปานกลาง]",
            "LOW": "🟢 [ทั่วไป]"
        }.get(urgency, "⚠️ [แจ้งเหตุ]")

        loc = case.get("location", {})
        province = loc.get("province") or "ไม่ระบุ"
        district = loc.get("district") or "ไม่ระบุ"
        subdistrict = loc.get("subdistrict") or "ไม่ระบุ"
        water_level = case.get("water_level") or "ไม่ระบุ"
        needs_str = ", ".join(case.get("needs", [])) or "ไม่ได้ระบุ"

        message = (
            f"{urgency_tag} ตรวจพบเคสน้ำท่วม\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"🌊 ระดับน้ำ: {water_level}\n"
            f"📍 พื้นที่: จ.{province} อ.{district} ต.{subdistrict}\n"
            f"🏠 จุดสังเกต: {loc.get('landmark_detail') or loc.get('village_or_community') or '-'}\n"
            f"📦 ต้องการ: {needs_str}\n"
            f"👥 กลุ่มเสี่ยง: {case.get('headcount') or 'ไม่ระบุ'}\n"
            f"📞 ติดต่อ: {case.get('contact_info') or 'ไม่ระบุ'}\n"
            f"📝 สรุป: {case.get('summary') or '-'}\n"
            f"🔗 แหล่งที่มา: {case.get('source_url', '')}"
        )

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "disable_web_page_preview": False
        }

        try:
            import requests
            res = requests.post(url, json=payload, timeout=10)
            return res.status_code == 200
        except Exception as e:
            print(f"Telegram alert error: {e}")
            return False
