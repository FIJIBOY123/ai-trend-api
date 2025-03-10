from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API Keys and Configurations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "TrendAnalysisBot/1.0")
APIFY_API_KEY = os.getenv("APIFY_API_KEY")

# Platform-specific configurations
REDDIT_SUBREDDITS = ["all", "popular", "trendingsubreddits"]
GOOGLE_TRENDS_TIMEFRAME = "now 7-d"
TIKTOK_TRENDING_HASHTAGS_LIMIT = 20

# Analysis configurations
TREND_ANALYSIS_PROMPT = """
Analyze the following trend data and provide insights:
- Calculate the growth rate and popularity score
- Predict the trend's future trajectory (grow, decline, plateau)
- Suggest actionable business strategies
- Estimate the trend's lifespan

Trend data: {trend_data}
"""

class Settings:
    PROJECT_NAME = "AI Trend Analysis API"
    VERSION = "1.0.0"
    API_V1_STR = "/api/v1"
    
    # FastAPI configurations
    BACKEND_CORS_ORIGINS = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",  # React frontend if needed
    ] 