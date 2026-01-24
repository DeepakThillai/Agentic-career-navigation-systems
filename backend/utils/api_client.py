"""
Shared API client with retry logic and rate limiting
"""

import requests
import time
import json
from typing import Dict, Any, Optional

class APIClient:
    """API client with exponential backoff retry logic"""
    
    MAX_RETRIES = 8  # Increased from 5 to 8
    BASE_WAIT = 8    # Increased from 4 to 8 seconds
    MIN_INTERVAL = 2  # Increased from 1.5 to 2 seconds
    
    _last_request_time = 0
    
    @classmethod
    def call_groq_api(cls, 
                      api_key: str, 
                      model: str,
                      messages: list,
                      temperature: float = 0.3,
                      max_tokens: int = 2000) -> Dict[str, Any]:
        """
        Call Groq API with retry logic and rate limiting
        
        Args:
            api_key: Groq API key
            model: Model name
            messages: List of messages
            temperature: Temperature setting
            max_tokens: Max tokens in response
            
        Returns:
            API response JSON
            
        Raises:
            Exception: If all retries fail
        """
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        last_error = None
        
        for attempt in range(cls.MAX_RETRIES):
            try:
                # Apply minimum interval throttling
                elapsed = time.time() - cls._last_request_time
                if elapsed < cls.MIN_INTERVAL:
                    time.sleep(cls.MIN_INTERVAL - elapsed)
                
                cls._last_request_time = time.time()
                
                response = requests.post(url, headers=headers, json=payload)
                
                # Success
                if response.status_code == 200:
                    return response.json()
                
                # Rate limit - retry with backoff
                if response.status_code == 429:
                    if attempt < cls.MAX_RETRIES - 1:
                        wait_time = cls.BASE_WAIT * (2 ** attempt)
                        print(f"  [429 Rate Limited] Waiting {wait_time}s before retry {attempt + 1}/{cls.MAX_RETRIES}...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"  [ERROR] Max retries reached with 429 errors")
                        response.raise_for_status()
                
                # Other errors
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                last_error = e
                if attempt < cls.MAX_RETRIES - 1:
                    wait_time = cls.BASE_WAIT * (2 ** attempt)
                    print(f"  [Retry {attempt + 1}/{cls.MAX_RETRIES}] Error: {type(e).__name__}. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise
        
        if last_error:
            raise last_error
        
        raise Exception("Max retries exceeded")
