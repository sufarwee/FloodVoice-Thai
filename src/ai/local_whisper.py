import os
from pathlib import Path
from typing import Optional

_local_whisper_instance = None
_loaded_model_name = None

def get_local_whisper_model(model_size: str = "base"):
    """
    โหลดโมเดล Faster-Whisper ในเครื่อง Mac/PC แบบ Singleton (โหลดครั้งเดียวใช้ซ้ำได้)
    """
    global _local_whisper_instance, _loaded_model_name

    if _local_whisper_instance is not None and _loaded_model_name == model_size:
        return _local_whisper_instance

    try:
        from faster_whisper import WhisperModel
        print(f"-> กำลังเตรียมโมเดล Local Mac Whisper ({model_size})...")
        # บน Mac Apple Silicon / CPU ใช้ compute_type="int8" หรือ "float32" เพื่อความเร็วและประหยัดแรม
        _local_whisper_instance = WhisperModel(model_size, device="cpu", compute_type="int8")
        _loaded_model_name = model_size
        return _local_whisper_instance
    except ImportError:
        print("คำเตือน: ยังไม่ได้ติดตั้ง faster-whisper สำหรับรัน Local Mac Whisper")
        print(">> ติดตั้งด้วยคำสั่ง: pip install faster-whisper")
        return None
    except Exception as e:
        print(f"ข้อผิดพลาดในการโหลดโมเดล Local Whisper: {e}")
        return None

def transcribe_local_mac(audio_path: str, model_size: str = "base") -> str:
    """
    ถอดเสียงภาษาไทยในเครื่อง Mac แบบออฟไลน์ 100% ฟรี ไม่ต้องต่อเน็ต ไม่เสียค่า API
    """
    if not audio_path or not os.path.exists(audio_path):
        return ""

    model = get_local_whisper_model(model_size)
    if not model:
        return ""

    try:
        segments, info = model.transcribe(audio_path, language="th", beam_size=5)
        text = "".join([s.text for s in segments]).strip()
        return text
    except Exception as e:
        print(f"ข้อผิดพลาดขณะถอดเสียงด้วย Local Whisper: {e}")
        return ""
