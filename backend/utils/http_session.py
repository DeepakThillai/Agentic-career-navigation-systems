"""
HTTP session with automatic rate limiting and retry logic for Groq API
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time

class RateLimitedSession(requests.Session):
    """Session with global request throttling"""
    
    last_request_time = 0
    min_interval = 1.5  # Minimum 1.5 seconds between requests
    
    def request(self, *args, **kwargs):
        """Override request to add throttling"""
        # Throttle requests
        elapsed = time.time() - self.__class__.last_request_time
        if elapsed < self.__class__.min_interval:
            time.sleep(self.__class__.min_interval - elapsed)
        
        self.__class__.last_request_time = time.time()
        return super().request(*args, **kwargs)


def get_groq_session():
    """Get a requests session configured for Groq API with retry logic"""
    session = RateLimitedSession()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST", "GET"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session
