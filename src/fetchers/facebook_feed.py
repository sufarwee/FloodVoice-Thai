from typing import List, Optional
from config import APIFY_TOKEN
from .base import BaseFetcher, SocialFeedItem

class FacebookFetcher(BaseFetcher):
    def __init__(self, apify_token: Optional[str] = None):
        self.apify_token = apify_token or APIFY_TOKEN

    def search_by_keywords(self, keywords: List[str], max_results: int = 5) -> List[SocialFeedItem]:
        results: List[SocialFeedItem] = []
        if not self.apify_token:
            return results

        try:
            from apify_client import ApifyClient
            client = ApifyClient(self.apify_token)
            
            # ใช้ Facebook Scraper Actor บน Apify
            query = " ".join(keywords)
            run_input = {
                "startUrls": [{"url": f"https://www.facebook.com/search/videos/?q={query}"}],
                "resultsLimit": max_results,
            }
            run = client.actor("apify/facebook-posts-scraper").call(run_input=run_input, timeout_secs=60)
            if run and "defaultDatasetId" in run:
                for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                    url = item.get("url") or item.get("postUrl")
                    if not url:
                        continue
                    results.append(SocialFeedItem(
                        platform="Facebook",
                        url=url,
                        title=item.get("text", "")[:80],
                        caption=item.get("text", ""),
                        is_live="live" in url.lower(),
                        thumbnail_url=item.get("media", [{}])[0].get("url") if item.get("media") else None,
                        author=item.get("user", {}).get("name"),
                        published_at=item.get("time")
                    ))
        except Exception as e:
            print(f"Facebook fetch error: {e}")

        return results
