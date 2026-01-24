"""
API Key Manager - Manages multiple Groq API keys for load distribution
Distributes keys across agents to avoid rate limiting
"""

import os
from typing import List, Dict, Any
import json


class APIKeyManager:
    """Manages multiple API keys and distributes them across agents"""
    
    # Agent names for key assignment
    AGENT_NAMES = [
        "StudentProfilingAgent",
        "GoalInterpretationAgent", 
        "ReadinessAssessmentAgent",
        "MarketIntelligenceAgent",
        "CareerPathPlanningAgent",
        "ReroutingAgent",
        "ActionRecommendationAgent",
        "FeedbackLearningAgent"
    ]
    
    def __init__(self):
        """Initialize API key manager and load all available keys"""
        self.keys: List[str] = []
        self.agent_key_map: Dict[str, str] = {}
        self.current_index = 0
        
        self._load_api_keys()
        self._assign_keys_to_agents()
    
    def _load_api_keys(self) -> None:
        """
        Load all available API keys from environment
        Supports: GROQ_API_KEY_1, GROQ_API_KEY_2, ..., GROQ_API_KEY_N
        or single key: GROQ_API_KEY (fallback)
        """
        # Try to load numbered keys first
        key_index = 1
        while True:
            key_var = f"GROQ_API_KEY_{key_index}"
            api_key = os.getenv(key_var)
            if not api_key:
                break
            self.keys.append(api_key)
            key_index += 1
        
        # If no numbered keys, try single key as fallback
        if not self.keys:
            api_key = os.getenv("GROQ_API_KEY") or "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"
            if api_key:
                self.keys.append(api_key)
        
        if not self.keys:
            raise ValueError("No API keys found!")
        
        print(f"✓ Loaded {len(self.keys)} API key(s)")
    
    def _assign_keys_to_agents(self) -> None:
        """Assign API keys to agents in round-robin fashion"""
        for i, agent_name in enumerate(self.AGENT_NAMES):
            key_index = i % len(self.keys)
            self.agent_key_map[agent_name] = self.keys[key_index]
        
        # Print assignment for debugging
        for agent_name in self.AGENT_NAMES:
            key_num = self.keys.index(self.agent_key_map[agent_name]) + 1
            print(f"  {agent_name}: Key #{key_num}")
    
    def get_key_for_agent(self, agent_name: str) -> str:
        """
        Get assigned API key for a specific agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            API key string
        """
        if agent_name not in self.agent_key_map:
            # Fallback to round-robin if agent not in map
            key = self.keys[self.current_index % len(self.keys)]
            self.current_index += 1
            return key
        
        return self.agent_key_map[agent_name]
    
    def get_next_key(self) -> str:
        """
        Get next API key in round-robin fashion
        Use this for general purpose API calls
        
        Returns:
            API key string
        """
        key = self.keys[self.current_index % len(self.keys)]
        self.current_index += 1
        return key
    
    def get_all_keys(self) -> List[str]:
        """Get all loaded API keys"""
        return self.keys.copy()
    
    def get_key_count(self) -> int:
        """Get number of available API keys"""
        return len(self.keys)
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of API key manager"""
        return {
            "total_keys": len(self.keys),
            "agent_assignments": self.agent_key_map,
            "key_rotation_index": self.current_index
        }


# Global instance
_key_manager: APIKeyManager = None


def get_key_manager() -> APIKeyManager:
    """Get or create the global API key manager"""
    global _key_manager
    if _key_manager is None:
        _key_manager = APIKeyManager()
    return _key_manager


def initialize_key_manager() -> APIKeyManager:
    """Initialize the API key manager"""
    global _key_manager
    _key_manager = APIKeyManager()
    return _key_manager
