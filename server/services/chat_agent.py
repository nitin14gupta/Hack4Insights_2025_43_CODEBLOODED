import json
import logging
from google.genai import types
from server.utils.llm_utils import get_llm_client, LLMConfig

logger = logging.getLogger(__name__)

class BearCartChatAgent:
    """AI Assistant for BearCart Dashboard using Google GenAI"""

    def __init__(self):
        self.client = get_llm_client()
        
    def ask(self, question: str, context_data: dict) -> dict:
        """
        Ask the AI a question about the dashboard data.
        """
        
        context_str = json.dumps(context_data, indent=2)
        
        system_prompt = f"""
        You are BearCart AI, an expert e-commerce data analyst. 
        Your goal is to help the user understand their business performance based on the provided data.
        
        DATA CONTEXT:
        {context_str}
        
        INSTRUCTIONS:
        1. Answer the user's question using ONLY the provided data.
        2. If the data describes a specific metric (e.g., revenue, conversion), cite the exact numbers.
        3. Be concise, professional, and insightful.
        4. If the user asks for a visualization or if a chart would clearly help, provide a JSON description of the chart in a specific format.
        
        RESPONSE FORMAT:
        You must return a valid JSON object with the following structure:
        {{
            "answer": "Your text answer here in markdown format.",
            "chart": {{ (OPTIONAL, set to null if not needed)
                "type": "bar" | "line" | "pie",
                "title": "Chart Title",
                "labels": ["Label1", "Label2"],
                "data": [10, 20]
            }}
        }}

        Output purely the JSON string.
        """

        try:
            response = self.client.models.generate_content(
                model=LLMConfig.MODEL_NAME,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=system_prompt + "\n\nUser Question: " + question)
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json" 
                )
            )
            
            content = response.text.strip()
            
            # Additional safety cleanup if defaults fail
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"GenAI Error: {e}")
            return {
                "answer": f"I'm sorry, I encountered an error: {str(e)}",
                "chart": None
            }

    def generate_strategic_insights(self, context_data: dict) -> dict:
        """
        Generate high-level strategic insights based on the data.
        """
        context_str = json.dumps(context_data, indent=2)
        
        system_prompt = f"""
        You are BearCart Strategist, a C-level e-commerce advisor.
        Analyze the provided data and generate a strategic executive summary.
        
        DATA CONTEXT:
        {context_str}
        
        INSTRUCTIONS:
        1. Identify 3 major "Growth Opportunities" (e.g., underperforming high-margin channels, mobile conversion fixes).
        2. Identify 3 "Critical Risks" (e.g., high refund rates in specific categories, reliance on single traffic source).
        3. Be extremely specific. Cite numbers from the data.
        4. Use a "punchy", confident tone.
        
        RESPONSE FORMAT:
        {{
            "opportunities": [
                {{ "title": "...", "description": "...", "impact": "High" }},
                ...
            ],
            "risks": [
                {{ "title": "...", "description": "...", "severity": "Critical" }},
                ...
            ]
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=LLMConfig.MODEL_NAME,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=system_prompt)
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json" 
                )
            )
            
            content = response.text.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"GenAI Insights Error: {e}")
            return {
                "opportunities": [{"title": "Analysis Failed", "description": "AI unavailable.", "impact": "Low"}],
                "risks": []
            }
