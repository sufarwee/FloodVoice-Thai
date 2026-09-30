from typing import List, Optional
from config import APIFY_TOKEN
from .base import BaseFetcher, SocialFeedItem

class InstagramFetcher(BaseFetcher):
    """
    ดึงโพสต์และ Reels ล่าสุดจาก Instagram ตามแฮชแท็ก (#น้ำท่วม) ผ่าน Apify Actor
    """
    def __init__(self, apify_token: Optional[str] = None):
        self.apify_token = apify_token or APIFY_TOKEN

    def search_by_keywords(self, keywords: List[str], max_results: int = 5) -> List[SocialFeedItem]:
        results: List[SocialFeedItem] = []
        if not self.apify_token:
            return results

        try:
            from apify_client import ApifyClient
            client = ApifyClient(self.apify_token)

            # ใช้ Apify Instagram Hashtag/Reels Scraper Actor
            # ตัดช่องว่างออกสำหรับค้นหาเป็นแฮชแท็ก เช่น #น้ำท่วม
            tag = keywords[0].replace("#", "").strip() if keywords else "น้ำท่วม"
            run_input = {
                "hashtags": [tag],
                "resultsLimit": max_results,
            }
            run = client.actor("apify/instagram-hashtag-scraper").call(run_input=run_input, timeout_secs=60)
            if run and "defaultDatasetId" in run:
                for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                    url = item.get("url") or item.get("postUrl")
                    if not url:
                        shortcode = item.get("shortCode")
                        if shortcode:
                            url = f"https://www.instagram.com/p/{shortcode}/"
                        else:
                            continue

                    caption = item.get("caption", "") or ""
                    results.append(SocialFeedItem(
                        platform="Instagram",
                        url=url,
                        title=caption[:80] if caption else "Instagram Post",
                        caption=caption,
                        is_live=False,
                        thumbnail_url=item.get("displayUrl"),
                        author=item.get("ownerUsername"),
                        published_at=str(item.get("timestamp", ""))
                    ))
        except Exception as e:
            print(f"Instagram fetch error: {e}")

        return results
