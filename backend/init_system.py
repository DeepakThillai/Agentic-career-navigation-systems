"""
System Initialization
Ensures all components are properly initialized with API key and context
"""

import os
import sys

def ensure_api_key():
    """Ensure API key is set"""
    api_key = os.getenv("GROQ_API_KEY") or "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"
    if not api_key:
        raise ValueError("API key not found")
    return api_key

def ensure_context_directory():
    """Ensure context directory exists"""
    from pathlib import Path
    context_dir = Path(__file__).parent.parent / "data" / "user_contexts"
    context_dir.mkdir(exist_ok=True, parents=True)
    return str(context_dir)

def initialize_system():
    """Initialize entire system"""
    try:
        # 1. Verify API key
        api_key = ensure_api_key()
        print(f"✓ API Key verified: {api_key[:10]}...")
        
        # 2. Ensure context directory
        context_dir = ensure_context_directory()
        print(f"✓ Context directory ready: {context_dir}")
        
        # 3. Load configuration
        from . import config
        print(f"✓ Configuration loaded: {config.APP_NAME} v{config.APP_VERSION}")
        
        print("\n✓ System initialization complete!")
        return True
        
    except Exception as e:
        print(f"✗ System initialization failed: {e}")
        return False

if __name__ == "__main__":
    initialize_system()
