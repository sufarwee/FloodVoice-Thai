from typing import List, Optional
from config import APIFY_TOKEN
from .base import BaseFetcher, SocialFeedItem

class TikTokFetcher(BaseFetcher):
    def __init__(self, apify_token: Optional[str] = None):
        self.apify_token = apify_token or APIFY_TOKEN

    def search_by_keywords(self, keywords: List[str], max_results: int = 5) -> List[SocialFeedItem]:
        results: List[SocialFeedItem] = []
        if not self.apify_token:
            # ถ้าไม่มี Apify token คืนค่า empty หรือใช้ fallback feed
            return results

        try:
            from apify_client import ApifyClient
            client = ApifyClient(self.apify_token)
            
            # ใช้ TikTok Scraper Actor บน Apify
            run_input = {
                "searchQueries": keywords[:2],
                "resultsPerPage": max_results,
                "searchSection": "/video"
            }
            run = client.actor("clockworks/free-tiktok-scraper").call(run_input=run_input, timeout_secs=60)
            if run and "defaultDatasetId" in run:
                for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                    url = item.get("webVideoUrl") or item.get("videoUrl")
                    if not url:
                        continue
                    results.append(SocialFeedItem(
                        platform="TikTok",
                        url=url,
                        title=item.get("text", "")[:80],
                        caption=item.get("text", ""),
                        is_live=item.get("isLive", False),
                        thumbnail_url=item.get("videoMeta", {}).get("coverUrl"),
                        author=item.get("authorMeta", {}).get("name"),
                        published_at=str(item.get("createTime", ""))
                    ))
        except Exception as e:
            print(f"TikTok fetch error: {e}")

        return results
