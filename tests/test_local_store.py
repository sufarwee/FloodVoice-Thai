import unittest
import tempfile
import shutil
from pathlib import Path
from database.local_store import LocalStore

class TestLocalStore(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_file = Path(self.test_dir) / "test_store.db"
        self.store = LocalStore(db_path=self.db_file)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_local_store_workflow(self):
        test_url = "https://youtube.com/watch?v=sample123"
        self.assertFalse(self.store.is_url_seen(test_url))

        self.store.mark_url_seen(test_url, platform="YouTube")
        self.assertTrue(self.store.is_url_seen(test_url))

        case_data = {
            "source_url": test_url,
            "platform": "YouTube",
            "is_distress": True,
            "urgency_level": "CRITICAL",
            "water_level": "ระดับอก",
            "water_level_code": "LEVEL_4_CRITICAL",
            "location": {
                "province": "เชียงราย",
                "district": "แม่สาย",
                "subdistrict": "เวียงพางคำ",
                "village_or_community": "เกาะทราย"
            },
            "needs": ["เรือ", "น้ำดื่ม"],
            "headcount": "2 คน",
            "contact_info": "089-999-9999",
            "summary": "น้ำท่วมเชียงราย",
            "case_status": "OPEN"
        }

        self.assertTrue(self.store.save_case(case_data))
        all_cases = self.store.get_all_cases()
        self.assertEqual(len(all_cases), 1)
        self.assertEqual(all_cases[0]["province"], "เชียงราย")
        self.assertIn("เรือ", all_cases[0]["needs"])

if __name__ == "__main__":
    unittest.main()
