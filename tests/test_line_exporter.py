import unittest
from src.exporters.line_bot import LineExporter

class TestLineExporter(unittest.TestCase):
    def test_line_exporter_initialization(self):
        exporter = LineExporter(channel_access_token="test_token", notify_token="test_notify")
        self.assertEqual(exporter.channel_access_token, "test_token")
        self.assertEqual(exporter.notify_token, "test_notify")

    def test_send_without_token(self):
        exporter = LineExporter(channel_access_token="", notify_token="")
        self.assertFalse(exporter.send_line_notify("Test message"))
        self.assertFalse(exporter.send_flex_message("user_123", {"urgency": "HIGH"}))

if __name__ == "__main__":
    unittest.main()
