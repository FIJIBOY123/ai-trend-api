from typing import Dict, Any, List
import openai
from config import OPENAI_API_KEY, TREND_ANALYSIS_PROMPT

class TrendAnalyzer:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY

    async def analyze_trend(self, trend_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single trend using GPT-4 and return structured insights
        """
        # Prepare the prompt with trend data
        prompt = TREND_ANALYSIS_PROMPT.format(trend_data=str(trend_data))
        
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a trend analysis expert. Analyze the provided trend data and give specific, actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract and structure the GPT-4 response
            analysis = response.choices[0].message.content
            
            # Parse the analysis into structured format
            return self._structure_analysis(analysis, trend_data)
        
        except Exception as e:
            return {
                "error": f"Failed to analyze trend: {str(e)}",
                "raw_trend_data": trend_data
            }

    async def analyze_multiple_trends(self, trends: List[Dict[str, Any]], platform: str) -> List[Dict[str, Any]]:
        """
        Analyze multiple trends from a specific platform
        """
        analyzed_trends = []
        for trend in trends:
            trend["platform"] = platform
            analysis = await self.analyze_trend(trend)
            analyzed_trends.append(analysis)
        return analyzed_trends

    def _structure_analysis(self, analysis_text: str, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert GPT-4's text analysis into structured JSON format
        """
        # Extract key metrics from the analysis text using simple parsing
        # This is a basic implementation - could be enhanced with better parsing
        growth_rate = "high" if "growing rapidly" in analysis_text.lower() else "medium" if "steady growth" in analysis_text.lower() else "low"
        
        # Determine predicted lifespan
        if "long-term" in analysis_text.lower():
            lifespan = "long"
        elif "short-lived" in analysis_text.lower():
            lifespan = "short"
        else:
            lifespan = "medium"

        # Calculate popularity score (0-100)
        popularity_score = self._calculate_popularity_score(original_data)

        return {
            "platform": original_data.get("platform", "unknown"),
            "topic": original_data.get("topic", ""),
            "popularity_score": popularity_score,
            "growth_rate": growth_rate,
            "predicted_lifespan": lifespan,
            "actionable_insight": analysis_text.split("actionable insight:")[-1].strip() if "actionable insight:" in analysis_text else analysis_text,
            "raw_metrics": original_data
        }

    def _calculate_popularity_score(self, trend_data: Dict[str, Any]) -> int:
        """
        Calculate a normalized popularity score based on platform-specific metrics
        """
        score = 0
        
        # Reddit-specific scoring
        if "mentions" in trend_data:
            score += min(trend_data["mentions"] / 1000, 50)  # Max 50 points from mentions
            if "comments" in trend_data:
                score += min(trend_data["comments"] / 100, 50)  # Max 50 points from comments

        # Twitter-specific scoring
        elif "engagement" in trend_data:
            engagement = trend_data["engagement"]
            score += min((engagement.get("retweets", 0) + engagement.get("likes", 0)) / 1000, 100)

        # TikTok-specific scoring
        elif "stats" in trend_data:
            stats = trend_data["stats"]
            total_engagement = (
                stats.get("likes", 0) + 
                stats.get("shares", 0) * 2 + 
                stats.get("comments", 0) * 3
            )
            score += min(total_engagement / 10000, 100)

        # Google Trends scoring
        elif "average_interest" in trend_data:
            score = trend_data["average_interest"]

        return min(int(score), 100)  # Ensure score is between 0 and 100 