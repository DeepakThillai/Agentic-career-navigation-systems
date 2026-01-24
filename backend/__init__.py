"""Backend package for Career Navigation System"""

import os
import requests
import time

# Verify at least one API key is set (single or numbered)
# Fallback to hardcoded key if not set in environment
HARDCODED_KEY = "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"
has_single_key = os.getenv("GROQ_API_KEY") is not None or HARDCODED_KEY
has_numbered_key = os.getenv("GROQ_API_KEY_1") is not None

if not (has_single_key or has_numbered_key):
    raise ValueError("No API keys found!")

# Global request throttling to prevent rate limiting
_last_request_time = 0
_min_request_interval = 1.5

# Store original post method
_original_post = requests.post

def _throttled_post(*args, **kwargs):
    """Wrapper around requests.post with throttling and exponential backoff"""
    global _last_request_time
    
    # Only throttle Groq API requests
    url = args[0] if args else kwargs.get('url', '')
    is_groq = 'groq.com' in str(url)
    
    if is_groq:
        # Apply global throttling
        elapsed = time.time() - _last_request_time
        if elapsed < _min_request_interval:
            time.sleep(_min_request_interval - elapsed)
        _last_request_time = time.time()
        
        # Exponential backoff retry for rate limits
        max_retries = 5
        base_wait = 4
        
        for attempt in range(max_retries):
            try:
                response = _original_post(*args, **kwargs)
                if response.status_code != 429:
                    return response
                
                # 429 rate limit - wait and retry
                if attempt < max_retries - 1:
                    wait_time = base_wait * (2 ** attempt)  # 4, 8, 16, 32, 64
                    time.sleep(wait_time)
                    _last_request_time = time.time()
                else:
                    return response  # Return last attempt even if 429
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = base_wait * (2 ** attempt)
                    time.sleep(wait_time)
                    _last_request_time = time.time()
                else:
                    raise
        
        return response
    
    return _original_post(*args, **kwargs)

# Monkey-patch requests.post
requests.post = _throttled_post
