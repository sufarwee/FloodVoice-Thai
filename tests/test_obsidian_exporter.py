import unittest
import tempfile
import shutil
from pathlib import Path
from src.exporters.obsidian import ObsidianExporter

class TestObsidianExporter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.exporter = ObsidianExporter(export_dir=Path(self.test_dir))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_obsidian_export(self):
        case_data = {
            "source_url": "https://tiktok.com/@user/video/999",
            "platform": "TikTok",
            "is_distress": True,
            "urgency_level": "CRITICAL",
            "water_level": "ระดับคอ",
            "water_level_code": "LEVEL_4_CRITICAL",
            "location": {
                "province": "ปราจีนบุรี",
                "district": "กบินทร์บุรี",
                "subdistrict": "กบินทร์",
                "village_or_community": "หมู่ 4",
                "landmark_detail": "ใกล้โรงเรียนวัดท่าลาน"
            },
            "needs": ["เรือ", "ยารักษาโรค", "นมเด็ก"],
            "headcount": "ผู้ป่วยติดเตียง 1 คน",
            "contact_info": "081-111-2222",
            "summary": "น้ำท่วมระดับคอ มีผู้ป่วยติดเตียง",
            "case_status": "OPEN"
        }

        card_path = self.exporter.export_case_card(case_data)
        self.assertTrue(Path(card_path).exists())
        content = Path(card_path).read_text(encoding="utf-8")
        self.assertIn("กบินทร์บุรี", content)
        self.assertIn("ระดับคอ", content)
        self.assertIn("tags:", content)

        # ตรวจสอบการสร้าง Dashboard
        dashboard_files = list(Path(self.test_dir).glob("DASHBOARD_*.md"))
        self.assertEqual(len(dashboard_files), 1)
        dash_content = dashboard_files[0].read_text(encoding="utf-8")
        self.assertIn("ปราจีนบุรี", dash_content)
        self.assertIn("CRITICAL", dash_content)

if __name__ == "__main__":
    unittest.main()
