import os
from typing import Dict, Any, List, Optional
from config import GOOGLE_SHEET_ID, GOOGLE_SERVICE_ACCOUNT_FILE

SHEET_COLUMNS = [
    "เวลาที่พบ",
    "ระดับความเร่งด่วน",
    "ระดับน้ำ",
    "รหัสระดับน้ำ",
    "จังหวัด",
    "อำเภอ/เขต",
    "ตำบล/แขวง",
    "จุดสังเกต/หมู่บ้าน",
    "สิ่งที่ต้องการด่วน",
    "กลุ่มเสี่ยง/จำนวนคน",
    "เบอร์ติดต่อ",
    "สรุปสถานการณ์",
    "แพลตฟอร์ม",
    "ลิงก์ต้นทาง",
    "สถานะเคส"
]

class GoogleSheetsExporter:
    def __init__(
        self,
        sheet_id: Optional[str] = None,
        service_account_path: Optional[str] = None
    ):
        self.sheet_id = sheet_id or GOOGLE_SHEET_ID
        self.service_account_path = service_account_path or GOOGLE_SERVICE_ACCOUNT_FILE
        self.client = None
        self.sheet = None
        self._init_sheet()

    def _init_sheet(self):
        if not self.sheet_id or not os.path.exists(self.service_account_path):
            return

        try:
            import gspread
            from google.oauth2.service_account import Credentials

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_file(
                self.service_account_path,
                scopes=scopes
            )
            self.client = gspread.authorize(creds)
            spreadsheet = self.client.open_by_key(self.sheet_id)
            self.sheet = spreadsheet.sheet1

            # ตรวจสอบว่ามีแถวหัวตารางหรือยัง ถ้ายังไม่มีให้สร้าง
            header = self.sheet.row_values(1)
            if not header:
                self.sheet.append_row(SHEET_COLUMNS)
        except Exception as e:
            print(f"Note: Google Sheets init note: {e}")

    def append_case(self, case_dict: Dict[str, Any]) -> bool:
        if not self.sheet:
            return False

        loc = case_dict.get("location", {})
        needs_str = ", ".join(case_dict.get("needs", [])) or "ไม่ได้ระบุ"

        row = [
            case_dict.get("created_at", ""),
            case_dict.get("urgency_level", "MEDIUM"),
            case_dict.get("water_level", "ไม่ระบุ"),
            case_dict.get("water_level_code", ""),
            loc.get("province", "ไม่ระบุ"),
            loc.get("district", "ไม่ระบุ"),
            loc.get("subdistrict", "ไม่ระบุ"),
            f"{loc.get('village_or_community', '')} {loc.get('landmark_detail', '')}".strip(),
            needs_str,
            case_dict.get("headcount", "ไม่ระบุ"),
            case_dict.get("contact_info", "ไม่ระบุ"),
            case_dict.get("summary", ""),
            case_dict.get("platform", "Unknown"),
            case_dict.get("source_url", ""),
            case_dict.get("case_status", "OPEN")
        ]

        try:
            self.sheet.append_row(row)
            return True
        except Exception as e:
            print(f"Error appending to Google Sheet: {e}")
            return False
