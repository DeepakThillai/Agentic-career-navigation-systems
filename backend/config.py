"""
Global Configuration
Ensures all components use consistent settings and API configuration
"""

import os
from pathlib import Path

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Validate API key
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")

# LLM Configuration
LLM_MODEL = "llama-3.3-70b-versatile"
LLM_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Request Configuration
REQUEST_TIMEOUT = 30
REQUEST_THROTTLE_INTERVAL = 1.5  # seconds between requests
REQUEST_MAX_RETRIES = 5
REQUEST_RETRY_DELAYS = [4, 8, 16, 32, 64]  # exponential backoff in seconds

# Context Configuration
CONTEXT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "user_contexts"
)

# Create context directory if needed
Path(CONTEXT_DIR).mkdir(exist_ok=True, parents=True)

# Application Configuration
APP_NAME = "Career Navigation System"
APP_VERSION = "2.0"

# Agent Configuration
AGENTS = {
    "profiling": "Student Profiling Agent",
    "goal": "Goal Interpretation Agent",
    "readiness": "Readiness Assessment Agent",
    "market": "Market Intelligence Agent",
    "path": "Career Path Planning Agent",
    "rerouting": "Rerouting Agent",
    "actions": "Action Recommendation Agent",
    "feedback": "Feedback Learning Agent"
}

# Roadmap Configuration
ROADMAP_STEPS = 5  # Default number of steps in roadmap
ACTIONS_PER_STEP = 3  # Default number of actions per step
QUESTIONS_PER_ACTION = 5  # Questions to generate for each action
ACTION_SCORE_THRESHOLD = 0.5  # Score >= 0.5 means action is satisfied (50% passing)

print(f"✓ Configuration loaded: API key present, {len(AGENTS)} agents configured")
