"""
Centralized LLM utility using Google GenAI SDK
"""
import os
import logging
from typing import Optional
from google import genai
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)

class LLMConfig:
    """Configuration for LLM"""
    # Prioritize GEMINI_API_KEY as requested, fallback to GOOGLE_API_KEY, then OPENROUTER logic if needed (but user wants Gemini)
    API_KEY = os.getenv("GEMINI_API_KEY")
    # Using the user-requested model or a logical default
    MODEL_NAME = "gemini-2.5-flash" 

def get_llm_client() -> genai.Client:
    """
    Get a configured Google GenAI Client
    """
    if not LLMConfig.API_KEY:
         raise ValueError("GEMINI_API_KEY (or GOOGLE_API_KEY) is not set env")

    # If it happens to be an OpenRouter key starting with sk-or, this client won't work well
    # But user explicit asked for "switch from openrouter to gemini simple"
    
    masked_key = LLMConfig.API_KEY[:6] + "..." + LLMConfig.API_KEY[-4:]
    logger.info(f"Initialized Google GenAI Client with key: {masked_key}")

    return genai.Client(api_key=LLMConfig.API_KEY)