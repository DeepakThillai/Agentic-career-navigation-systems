"""
Centralized API utilities for rate limiting and retry logic
"""

import requests
import time
import os

# Global request throttling
last_request_time = 0
min_request_interval = 1.5  # 1.5 seconds between requests

def call_llm(prompt: str, max_tokens: int = 2000, retries: int = 5) -> str:
    """
    Call Groq LLM with built-in rate limiting and retry logic
    
    Args:
        prompt: The prompt to send to the LLM
        max_tokens: Maximum tokens in response
        retries: Number of retries on rate limit (default 5)
        
    Returns:
        Content from LLM response
        
    Raises:
        Exception: If all retries fail
    """
    global last_request_time
    
    api_key = os.getenv("GROQ_API_KEY") or "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"
    if not api_key:
        raise ValueError("API key not found")
    
    # Throttle requests globally to avoid rate limiting
    elapsed = time.time() - last_request_time
    if elapsed < min_request_interval:
        sleep_time = min_request_interval - elapsed
        time.sleep(sleep_time)
    
    for attempt in range(retries):
        try:
            last_request_time = time.time()
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": max_tokens
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Too Many Requests
                if attempt < retries - 1:
                    wait_time = 2 ** (attempt + 2)  # 4, 8, 16, 32, 64 seconds
                    print(f"Rate limited. Retrying in {wait_time}s... (Attempt {attempt + 1}/{retries})")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Rate limited after {retries} retries. API quota may be exhausted.")
            else:
                raise
        except Exception as e:
            if attempt < retries - 1:
                print(f"Error: {e}. Retrying... (Attempt {attempt + 1}/{retries})")
                time.sleep(3)
            else:
                raise
    
    raise Exception("Failed to get LLM response after all retries")
