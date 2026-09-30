from dataclasses import dataclass
from typing import Optional, List
from abc import ABC, abstractmethod

@dataclass
class SocialFeedItem:
    platform: str                  # 'YouTube', 'TikTok', 'Facebook', 'Instagram'
    url: str                       # ลิงก์ตรงของโพสต์หรือวิดีโอ
    title: str                     # ชื่อเรื่อง / หัวข้อ
    caption: str                   # ข้อความเนื้อหา
    is_live: bool = False          # ถ่ายทอดสดอยู่หรือไม่
    thumbnail_url: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[str] = None

class BaseFetcher(ABC):
    @abstractmethod
    def search_by_keywords(self, keywords: List[str], max_results: int = 5) -> List[SocialFeedItem]:
        """ค้นหาโพสต์และคลิปวิดีโอตามรายการ Keywords"""
        pass
