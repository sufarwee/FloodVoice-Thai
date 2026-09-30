import unittest
from src.ai.schemas import DistressReport, NormalizedLocation, UrgencyLevel, WaterLevelCode

class TestSchemas(unittest.TestCase):
    def test_distress_report_creation(self):
        loc = NormalizedLocation(
            is_bangkok=False,
            province="ปราจีนบุรี",
            district="กบินทร์บุรี",
            subdistrict="กบินทร์",
            village_or_community="หมู่ 3",
            landmark_detail="ข้างวัดท่าลาน"
        )
        report = DistressReport(
            is_distress=True,
            urgency_level=UrgencyLevel.CRITICAL,
            water_level="ระดับอก",
            water_level_code=WaterLevelCode.LEVEL_4_CRITICAL,
            location=loc,
            needs=["เรือพาย", "นมเด็ก", "ยาเบาหวาน"],
            headcount="ผู้ใหญ่ 3 เด็ก 1 ผู้ป่วยติดเตียง 1",
            contact_info="081-234-5678",
            summary="น้ำท่วมสูงถึงอก ติดอยู่ในบ้าน 5 คน ต้องการเรือและนมผงเด็กด่วน"
        )

        self.assertTrue(report.is_distress)
        self.assertEqual(report.urgency_level, UrgencyLevel.CRITICAL)
        self.assertEqual(report.water_level_code, WaterLevelCode.LEVEL_4_CRITICAL)
        self.assertEqual(report.location.province, "ปราจีนบุรี")
        self.assertIn("นมเด็ก", report.needs)

if __name__ == "__main__":
    unittest.main()
