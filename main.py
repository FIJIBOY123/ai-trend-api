from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any
import asyncio
from datetime import datetime

from scrapers import RedditScraper, GoogleTrendsScraper, TikTokScraper, TwitterScraper
from ai_analysis import TrendAnalyzer
from config import Settings

app = FastAPI(
    title=Settings.PROJECT_NAME,
    version=Settings.VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scrapers and analyzer
reddit_scraper = RedditScraper()
google_trends_scraper = GoogleTrendsScraper()
tiktok_scraper = TikTokScraper()
twitter_scraper = TwitterScraper()
trend_analyzer = TrendAnalyzer()

@app.get("/")
async def root():
    return {
        "message": "Welcome to the AI Trend Analysis API",
        "version": Settings.VERSION,
        "endpoints": [
            "/api/v1/trends/{platform}",
            "/api/v1/analyze",
            "/api/v1/analyze/{platform}"
        ]
    }

@app.get("/api/v1/trends/{platform}")
async def get_platform_trends(platform: str) -> Dict[str, Any]:
    """
    Get trending topics from a specific platform
    """
    try:
        if platform.lower() == "reddit":
            trends = reddit_scraper.get_trending_topics()
        elif platform.lower() == "google":
            trends = google_trends_scraper.get_trending_topics()
        elif platform.lower() == "tiktok":
            trends = await tiktok_scraper.get_trending_topics()
        elif platform.lower() == "twitter":
            trends = await twitter_scraper.get_trending_topics()
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")

        return {
            "platform": platform,
            "timestamp": datetime.now().isoformat(),
            "trends": trends
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analyze/{platform}")
async def analyze_platform_trends(platform: str) -> Dict[str, Any]:
    """
    Get and analyze trends from a specific platform
    """
    # First get the trends
    trends_response = await get_platform_trends(platform)
    trends = trends_response["trends"]

    # Then analyze them
    analyzed_trends = await trend_analyzer.analyze_multiple_trends(trends, platform)

    return {
        "platform": platform,
        "timestamp": datetime.now().isoformat(),
        "analyzed_trends": analyzed_trends
    }

@app.post("/api/v1/analyze")
async def analyze_trends(trends: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze provided trend data using GPT-4
    """
    try:
        analyzed_trends = []
        for trend in trends:
            analysis = await trend_analyzer.analyze_trend(trend)
            analyzed_trends.append(analysis)

        return {
            "timestamp": datetime.now().isoformat(),
            "analyzed_trends": analyzed_trends
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/trends")
async def get_all_trends() -> Dict[str, Any]:
    """
    Get trending topics from all platforms
    """
    try:
        # Gather trends from all platforms concurrently
        tasks = [
            get_platform_trends("reddit"),
            get_platform_trends("google"),
            get_platform_trends("tiktok"),
            get_platform_trends("twitter")
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_trends = {}
        for result in results:
            if isinstance(result, dict):
                platform = result["platform"]
                all_trends[platform] = result["trends"]
            else:
                # Handle any errors that occurred
                print(f"Error fetching trends: {str(result)}")

        return {
            "timestamp": datetime.now().isoformat(),
            "trends": all_trends
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 