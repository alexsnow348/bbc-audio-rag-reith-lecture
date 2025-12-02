"""
Recommendation engine for suggesting next content to listen to.
Uses Google Gemini AI to analyze listening patterns and recommend similar content.
"""

import google.generativeai as genai
from typing import List, Dict, Optional
from pathlib import Path
from config import Config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class RecommendationEngine:
    """Generates personalized content recommendations using AI"""
    
    def __init__(self):
        """Initialize recommendation engine with Gemini API"""
        self.api_key = Config.GOOGLE_AI_API_KEY
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel(Config.GOOGLE_MODEL)
                logger.info(f"Recommendation engine initialized with model: {Config.GOOGLE_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini API: {e}")
                self.model = None
        else:
            logger.warning("Google AI API key not configured")
    
    def is_ready(self) -> bool:
        """Check if recommendation engine is ready to use"""
        return self.model is not None
    
    def generate_recommendations(
        self, 
        completed_titles: List[str], 
        available_titles: List[str],
        listening_history: Optional[List[Dict]] = None,
        top_n: int = 5
    ) -> List[Dict[str, str]]:
        """
        Generate personalized recommendations based on listening history.
        
        Args:
            completed_titles: List of lecture titles the user has completed
            available_titles: List of all available lecture titles
            listening_history: Optional list of history records with metadata (access_count, dates, etc.)
            top_n: Number of recommendations to return
        
        Returns:
            List of dictionaries with 'title' and 'reason' keys
        """
        if not self.is_ready():
            return [{
                'title': 'API Not Configured',
                'reason': '❌ Google AI API key not configured. Please set GOOGLE_AI_API_KEY in .env file.'
            }]
        
        if not completed_titles:
            return [{
                'title': 'No History Yet',
                'reason': '📚 Start listening to some lectures first! Mark them as completed to get personalized recommendations.'
            }]
        
        if not available_titles:
            return [{
                'title': 'No Content Available',
                'reason': '❌ No lectures available to recommend. Please download some content first.'
            }]
        
        try:
            # Create prompt for AI
            prompt = self._create_recommendation_prompt(
                completed_titles, 
                available_titles, 
                listening_history,
                top_n
            )
            
            # Generate recommendations using Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the response
            recommendations = self._parse_recommendations(response.text)
            
            logger.info(f"Generated {len(recommendations)} recommendations")
            return recommendations[:top_n]
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return [{
                'title': 'Error',
                'reason': f'❌ Failed to generate recommendations: {str(e)}'
            }]
    
    def _create_recommendation_prompt(
        self, 
        completed_titles: List[str], 
        available_titles: List[str],
        listening_history: Optional[List[Dict]],
        top_n: int
    ) -> str:
        """Create a prompt for the AI to generate recommendations"""
        
        # Build completed lectures section with metadata if available
        if listening_history:
            completed_str = ""
            for record in listening_history:
                if record.get('status') == 'completed':
                    title = record['content_name']
                    access_count = record.get('access_count', 1)
                    completed_at = record.get('completed_at', 'N/A')
                    
                    # Add engagement indicator
                    engagement = "⭐⭐⭐" if access_count > 5 else "⭐⭐" if access_count > 2 else "⭐"
                    completed_str += f"- {title} {engagement} (listened {access_count}x, completed: {completed_at[:10]})\n"
        else:
            completed_str = "\n".join([f"- {title}" for title in completed_titles])
        
        available_str = "\n".join([f"- {title}" for title in available_titles[:200]])  # Limit to avoid token limits
        
        prompt = f"""You are a knowledgeable librarian helping someone discover their next lecture to listen to.

The user has completed these lectures (with engagement levels):
{completed_str}

Here are some available lectures they haven't completed yet:
{available_str}

Based on:
1. The themes, topics, and subjects in their completed lectures
2. Their engagement level (how many times they listened to each)
3. The chronological progression of their interests

Recommend the top {top_n} lectures from the available list that they would most enjoy next.

For each recommendation, provide:
1. The EXACT title from the available list (must match exactly)
2. A brief, engaging reason (1-2 sentences) explaining why this lecture fits their interests and listening patterns

Format your response EXACTLY like this (use this exact format with the pipe separator):
TITLE: [exact title] | REASON: [your explanation]
TITLE: [exact title] | REASON: [your explanation]
...

Focus on thematic connections, intellectual progression, and complementary topics. Consider their most-listened lectures as stronger interest indicators."""
        
        return prompt
    
    def _parse_recommendations(self, response_text: str) -> List[Dict[str, str]]:
        """Parse AI response into structured recommendations"""
        recommendations = []
        
        lines = response_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or not line.startswith('TITLE:'):
                continue
            
            try:
                # Parse format: TITLE: [title] | REASON: [reason]
                parts = line.split('|')
                if len(parts) >= 2:
                    title_part = parts[0].replace('TITLE:', '').strip()
                    reason_part = parts[1].replace('REASON:', '').strip()
                    
                    recommendations.append({
                        'title': title_part,
                        'reason': reason_part
                    })
            except Exception as e:
                logger.warning(f"Failed to parse recommendation line: {line}, error: {e}")
                continue
        
        return recommendations
    
    def format_recommendations_for_display(
        self, 
        recommendations: List[Dict[str, str]]
    ) -> str:
        """Format recommendations as markdown for Gradio display"""
        
        if not recommendations:
            return "No recommendations available."
        
        # Check for error states
        if recommendations[0]['title'] in ['API Not Configured', 'No History Yet', 'No Content Available', 'Error']:
            return f"### {recommendations[0]['title']}\n\n{recommendations[0]['reason']}"
        
        output = ["## 🎯 Recommended for You\n"]
        
        for i, rec in enumerate(recommendations, 1):
            output.append(f"### {i}. {rec['title']}")
            output.append(f"_{rec['reason']}_\n")
        
        return "\n".join(output)
