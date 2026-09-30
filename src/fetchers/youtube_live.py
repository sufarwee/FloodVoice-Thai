from typing import List, Optional
from config import YOUTUBE_API_KEY
from .base import BaseFetcher, SocialFeedItem

class YouTubeFetcher(BaseFetcher):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or YOUTUBE_API_KEY

    def search_by_keywords(self, keywords: List[str], max_results: int = 5) -> List[SocialFeedItem]:
        results: List[SocialFeedItem] = []
        query_str = " ".join(keywords)

        # 1. ถ้ามี YouTube Data API Key ให้ใช้ API ค้นหาทั้ง Live และ Recent Videos
        if self.api_key:
            try:
                results.extend(self._search_with_api(query_str, max_results=max_results))
            except Exception as e:
                print(f"YouTube Data API error: {e}, falling back to yt-dlp search...")

        # 2. ถ้าไม่มี API Key หรือ API ล้มเหลว ให้ใช้ yt-dlp search
        if not results:
            results.extend(self._search_with_ytdlp(query_str, max_results=max_results))

        return results

    def _search_with_api(self, query: str, max_results: int = 5) -> List[SocialFeedItem]:
        import requests
        items = []
        # ค้นหาทั้ง Live สด และวิดีโออัปเดตล่าสุด
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": max_results,
            "order": "date",
            "key": self.api_key
        }
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()

        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            video_id = item.get("id", {}).get("videoId")
            if not video_id:
                continue

            is_live = snippet.get("liveBroadcastContent") in ("live", "upcoming")
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            items.append(SocialFeedItem(
                platform="YouTube",
                url=video_url,
                title=snippet.get("title", ""),
                caption=snippet.get("description", ""),
                is_live=is_live,
                thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url"),
                author=snippet.get("channelTitle"),
                published_at=snippet.get("publishedAt")
            ))
        return items

    def _search_with_ytdlp(self, query: str, max_results: int = 5) -> List[SocialFeedItem]:
        items = []
        try:
            import yt_dlp
            ydl_opts = {
                "extract_flat": True,
                "quiet": True,
                "no_warnings": True,
                "default_search": f"ytsearch{max_results}"
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_res = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
                for entry in search_res.get("entries", []):
                    if not entry:
                        continue
                    video_url = entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id')}"
                    items.append(SocialFeedItem(
                        platform="YouTube",
                        url=video_url,
                        title=entry.get("title", ""),
                        caption=entry.get("description") or entry.get("title", ""),
                        is_live=entry.get("is_live", False),
                        thumbnail_url=entry.get("thumbnail"),
                        author=entry.get("channel") or entry.get("uploader"),
                        published_at=entry.get("upload_date")
                    ))
        except Exception as e:
            print(f"yt-dlp search error: {e}")
        return items
