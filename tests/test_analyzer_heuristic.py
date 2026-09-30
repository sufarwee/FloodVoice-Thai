import unittest
from src.ai.analyzer import MultimodalAnalyzer
from src.ai.schemas import UrgencyLevel, WaterLevelCode

class TestAnalyzerHeuristic(unittest.TestCase):
    def test_heuristic_analysis(self):
        analyzer = MultimodalAnalyzer()
        text = "ช่วยด้วยครับ ตอนนี้น้ำท่วมถึงอก แถวกบินทร์บุรี ปราจีนบุรี มีคนแก่ติดเตียง ต้องการเรือและอาหารด่วน"
        report = analyzer._heuristic_fallback(text)

        self.assertTrue(report.is_distress)
        self.assertEqual(report.urgency_level, UrgencyLevel.CRITICAL)
        self.assertEqual(report.water_level_code, WaterLevelCode.LEVEL_4_CRITICAL)
        self.assertEqual(report.location.province, "ปราจีนบุรี")
        self.assertIn("เรือพาย/เรือท้องแบน", report.needs)
        self.assertIn("อพยพผู้ป่วยติดเตียง/คนชรา", report.needs)

if __name__ == "__main__":
    unittest.main()
