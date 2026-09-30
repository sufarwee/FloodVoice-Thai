from typing import List, Optional
from config import APIFY_TOKEN
from .base import BaseFetcher, SocialFeedItem

class TwitterFetcher(BaseFetcher):
    """
    ดึงทวีตล่าสุดจาก X (Twitter) ตามคีย์เวิร์ดและแฮชแท็ก (#น้ำท่วม) ผ่าน Apify Actor
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

            # ใช้ Apify Twitter/X Scraper Actor (apidojo/tweet-scraper)
            query = " ".join(keywords)
            run_input = {
                "searchTerms": [query],
                "maxItems": max_results,
                "sort": "Latest"
            }
            run = client.actor("apidojo/tweet-scraper").call(run_input=run_input, timeout_secs=60)
            if run and "defaultDatasetId" in run:
                for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                    url = item.get("url") or item.get("twitterUrl")
                    if not url:
                        continue

                    # ตรวจสอบว่ามีลิงก์วิดีโอหรือรูปภาพแนบมาหรือไม่
                    media_list = item.get("media", [])
                    thumb_url = None
                    if media_list and isinstance(media_list, list):
                        thumb_url = media_list[0].get("media_url_https") or media_list[0].get("url")

                    text = item.get("text") or item.get("full_text", "")
                    results.append(SocialFeedItem(
                        platform="Twitter/X",
                        url=url,
                        title=text[:80],
                        caption=text,
                        is_live=False,
                        thumbnail_url=thumb_url,
                        author=item.get("author", {}).get("userName"),
                        published_at=item.get("createdAt")
                    ))
        except Exception as e:
            print(f"Twitter/X fetch error: {e}")

        return results
