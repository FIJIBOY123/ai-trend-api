from typing import List, Dict, Any
import praw
from pytrends.request import TrendReq
from apify_client import ApifyClient
import requests
from config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    APIFY_API_KEY,
    REDDIT_SUBREDDITS,
    GOOGLE_TRENDS_TIMEFRAME,
    TIKTOK_TRENDING_HASHTAGS_LIMIT
)

class RedditScraper:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )

    def get_trending_topics(self) -> List[Dict[str, Any]]:
        trends = []
        for subreddit_name in REDDIT_SUBREDDITS:
            subreddit = self.reddit.subreddit(subreddit_name)
            for post in subreddit.hot(limit=10):
                trends.append({
                    "topic": post.title,
                    "mentions": post.score,
                    "url": post.url,
                    "comments": post.num_comments,
                    "subreddit": subreddit_name
                })
        return trends

class GoogleTrendsScraper:
    def __init__(self):
        self.pytrends = TrendReq(hl='en-US', tz=360)

    def get_trending_topics(self) -> List[Dict[str, Any]]:
        # Get real-time trending searches
        trending_searches = self.pytrends.trending_searches(pn='united_states')
        trends = []
        
        for topic in trending_searches.values.tolist()[:10]:
            # Get more details about each trend
            self.pytrends.build_payload([topic[0]], timeframe=GOOGLE_TRENDS_TIMEFRAME)
            interest_over_time = self.pytrends.interest_over_time()
            
            if not interest_over_time.empty:
                trend_data = {
                    "topic": topic[0],
                    "interest_over_time": interest_over_time[topic[0]].tolist(),
                    "average_interest": interest_over_time[topic[0]].mean()
                }
                trends.append(trend_data)
        
        return trends

class TikTokScraper:
    def __init__(self):
        self.client = ApifyClient(APIFY_API_KEY)

    async def get_trending_topics(self) -> List[Dict[str, Any]]:
        # Use Apify's TikTok Scraper
        run_input = {
            "hashtag": "trending",
            "maxItems": TIKTOK_TRENDING_HASHTAGS_LIMIT
        }
        
        run = self.client.actor("clockworks/tiktok-scraper").call(run_input=run_input)
        items = []
        
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            items.append({
                "topic": item.get("desc", ""),
                "hashtags": item.get("hashtags", []),
                "stats": {
                    "likes": item.get("likesCount", 0),
                    "shares": item.get("shareCount", 0),
                    "comments": item.get("commentCount", 0)
                }
            })
        
        return items

class TwitterScraper:
    def __init__(self):
        self.client = ApifyClient(APIFY_API_KEY)

    async def get_trending_topics(self) -> List[Dict[str, Any]]:
        # Use Apify's Twitter Scraper
        run_input = {
            "searchTerms": ["trending"],
            "maxTweets": 100,
            "language": "en"
        }
        
        run = self.client.actor("quacker/twitter-scraper").call(run_input=run_input)
        trends = []
        
        for tweet in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            trends.append({
                "topic": tweet.get("full_text", ""),
                "engagement": {
                    "retweets": tweet.get("retweet_count", 0),
                    "likes": tweet.get("favorite_count", 0)
                },
                "created_at": tweet.get("created_at", "")
            })
        
        return trends 