import unittest
from src.ai.local_whisper import transcribe_local_mac
from src.ai.analyzer import MultimodalAnalyzer

class TestLocalWhisper(unittest.TestCase):
    def test_transcribe_nonexistent_audio(self):
        result = transcribe_local_mac("/nonexistent/audio.mp3")
        self.assertEqual(result, "")

    def test_analyzer_transcribe_audio_empty(self):
        analyzer = MultimodalAnalyzer()
        res = analyzer.transcribe_audio("/nonexistent/audio.mp3")
        self.assertEqual(res, "")

if __name__ == "__main__":
    unittest.main()
