import os
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple

class StreamSampler:
    """
    จัดการสกัดแทร็กเสียงและจับภาพคีย์เฟรมจากวิดีโอหรือ Live Stream ด้วย yt-dlp และ ffmpeg
    """

    @staticmethod
    def extract_audio_and_frames(
        media_url: str,
        output_dir: str,
        max_duration_seconds: int = 180,
        extract_frames: bool = True
    ) -> Tuple[Optional[str], List[str]]:
        """
        ดาวน์โหลดเฉพาะส่วนเสียงและภาพเฟรมตัวอย่างจาก URL
        คืนค่า: (audio_path, list_of_frame_paths)
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        audio_output = os.path.join(output_dir, "audio.mp3")
        frame_paths = []

        # กำหนดคอนฟิกของ yt-dlp สำหรับดาวน์โหลดเฉพาะเสียง (ไม่โหลดวิดีโอทั้งไฟล์ ประหยัด bandwidth)
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": os.path.join(output_dir, "temp_stream.%(ext)s"),
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }],
            "quiet": True,
            "no_warnings": True,
            # สำหรับ Live Stream หรือคลิปยาว ให้ตัดเอาเฉพาะช่วง 180 วินาทีแรก
            "postprocessor_args": [
                "-t", str(max_duration_seconds)
            ],
            # ป้องกัน bot detection เบื้องต้น
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        }

        try:
            import yt_dlp
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(media_url, download=True)
                temp_audio = os.path.join(output_dir, "temp_stream.mp3")
                if os.path.exists(temp_audio):
                    os.rename(temp_audio, audio_output)
                else:
                    audio_output = None

                # ดึง thumbnail ของคลิปเป็นเฟรมแรก
                thumb_url = info.get("thumbnail") if info else None
                if thumb_url and extract_frames:
                    thumb_path = os.path.join(output_dir, "thumbnail.jpg")
                    try:
                        import requests
                        r = requests.get(thumb_url, timeout=10)
                        if r.status_code == 200:
                            with open(thumb_path, "wb") as f:
                                f.write(r.content)
                            frame_paths.append(thumb_path)
                    except Exception as te:
                        print(f"Failed to fetch thumbnail: {te}")

        except Exception as e:
            print(f"Error extracting media from {media_url}: {e}")
            audio_output = None

        return audio_output, frame_paths

    @staticmethod
    def cleanup_directory(directory_path: str):
        """ลบไฟล์และไดเรกทอรีชั่วคราว"""
        try:
            if os.path.exists(directory_path):
                shutil.rmtree(directory_path)
        except Exception as e:
            print(f"Cleanup error: {e}")
