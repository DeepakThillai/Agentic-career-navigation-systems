"""
Career Path Planning Agent
Generates step-by-step career paths with primary and fallback routes
"""

import json
import os
from typing import Dict, Any
import requests
import uuid
from datetime import datetime
from ..user_context import UserContextManager
from ..utils.api_client import APIClient
from ..utils.api_key_manager import get_key_manager


class CareerPathPlanningAgent:
    """
    Creates detailed career paths considering profile, readiness, and market
    """
    
    AGENT_NAME = "Career Path Planning Agent"
    AGENT_OBJECTIVE = (
        "Generate a step-by-step career path. "
        "Consider student profile, goal readiness, and market feasibility. "
        "Produce primary path and fallback paths. "
        "Estimate success probability conservatively."
    )
    
    def __init__(self, context_manager: UserContextManager):
        """Initialize agent"""
        self.context_manager = context_manager
        key_manager = get_key_manager()
        self.api_key = key_manager.get_key_for_agent("CareerPathPlanningAgent")
    
    def _call_llm(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Groq LLM with agent-specific prompt"""
        
        output_schema = """{
  "career_path": {
    "path_id": "unique-path-id",
    "target_role": "Target Role",
    "estimated_duration_months": 12,
    "success_probability": 0.70,
    "primary_path": {
      "steps": [
        {
          "step_number": 1,
          "title": "Step Title",
          "description": "What to do",
          "skills_to_learn": ["skill1", "skill2"],
          "resources": ["resource1", "resource2"],
          "duration_weeks": 4,
          "success_criteria": "How to know you completed this",
          "difficulty": "easy/medium/hard"
        }
      ],
      "total_weeks": 16,
      "key_milestones": ["milestone1", "milestone2"]
    },
    "fallback_paths": [
      {
        "alternative_role": "Alternative Role",
        "reason": "Why this is a fallback",
        "easier_than_primary": true,
        "steps_summary": ["step1", "step2", "step3"]
      }
    ],
    "risk_factors": ["risk1", "risk2"],
    "confidence_boosters": ["action1", "action2"],
    "path_rationale": "Why this path was designed this way"
  }
}"""
        
        system_prompt = f"""You are an autonomous agent operating inside an Agentic AI–Powered Career Navigation System.

AGENT_NAME: {self.AGENT_NAME}

AGENT_OBJECTIVE: {self.AGENT_OBJECTIVE}

INPUT_JSON:
{json.dumps(input_data, indent=2)}

RESPONSIBILITIES:
- Design a realistic, step-by-step career path to the target role
- Each step should be specific and actionable
- Consider: current skill level, learning capacity, market requirements
- Estimate duration for each step (be realistic, not optimistic)
- Calculate overall success probability (0.0-1.0) conservatively
- Include 2-3 fallback alternative paths
- Identify risk factors that could derail the plan

SUCCESS PROBABILITY:
- Consider: skill gaps, market demand, student readiness, time commitment
- 0.7-1.0: High probability, strong fit
- 0.5-0.7: Moderate probability, requires effort
- 0.3-0.5: Low probability, challenging path
- 0.0-0.3: Very low probability, consider alternatives

PATH DESIGN PRINCIPLES:
- Start with foundational skills
- Build progressively toward advanced topics
- Include practical projects at each stage
- Each step should take 2-6 weeks
- Total path should be 8-24 weeks
- Be conservative with timeframes

FALLBACK PATHS:
- Easier roles that use similar skills
- Roles with lower entry barriers
- Roles student is better prepared for

OUTPUT_SCHEMA:
{output_schema}

Return ONLY valid JSON matching the schema. No markdown, no explanations."""

        try:
            result = APIClient.call_groq_api(
                api_key=self.api_key,
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.5,
                max_tokens=3000
            )
            
            content = result["choices"][0]["message"]["content"]
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
            
        except Exception as e:
            print(f"LLM call error: {e}")
            raise
    
    def generate_path(self, 
                     user_id: str,
                     duration_weeks: int = 12) -> Dict[str, Any]:
        """
        Generate career path for user
        
        Args:
            user_id: User identifier
            duration_weeks: Available time for learning
            
        Returns:
            Complete career path with primary and fallback routes
        """
        
        # Load context
        context = self.context_manager.load_context(user_id)
        
        # Validate prerequisites
        if not context["career_goals"].get("interpreted_goal"):
            return {
                "agent": self.AGENT_NAME,
                "status": "error",
                "message": "Missing interpreted goal. Run Goal Interpretation Agent first."
            }
        
        if not context["readiness"].get("confidence_score"):
            return {
                "agent": self.AGENT_NAME,
                "status": "error",
                "message": "Missing readiness assessment. Run Readiness Assessment Agent first."
            }
        
        if not context["market_context"].get("target_role_analysis"):
            return {
                "agent": self.AGENT_NAME,
                "status": "error",
                "message": "Missing market analysis. Run Market Intelligence Agent first."
            }
        
        # Prepare comprehensive input
        input_data = {
            "target_role": context["career_goals"]["interpreted_goal"],
            "student_profile": context["student_profile"],
            "readiness_assessment": context["readiness"],
            "market_analysis": context["market_context"]["target_role_analysis"],
            "available_duration_weeks": duration_weeks,
            "previous_attempts": context["reroute_history"].get("failed_paths", [])
        }
        
        # Call LLM
        result = self._call_llm(input_data)
        
        # Extract career path
        career_path = result["career_path"]
        
        # Add unique ID and timestamp
        path_id = str(uuid.uuid4())
        career_path["path_id"] = path_id
        
        # Update context with active path
        self.context_manager.update_active_path(user_id, {
            "path_id": path_id,
            "target_role": career_path["target_role"],
            "primary_path": career_path["primary_path"],
            "fallback_paths": career_path["fallback_paths"],
            "success_probability": career_path["success_probability"],
            "status": "not_started"
        })
        
        # Log interaction
        self.context_manager.log_agent_interaction(
            user_id,
            self.AGENT_NAME,
            "path_generated",
            {
                "path_id": path_id,
                "target_role": career_path["target_role"],
                "success_probability": career_path["success_probability"],
                "steps_count": len(career_path["primary_path"]["steps"])
            }
        )
        
        return {
            "agent": self.AGENT_NAME,
            "status": "success",
            "career_path": career_path,
            "context_updated": True
        }


# Example usage
if __name__ == "__main__":
    from ..user_context import UserContextManager
    
    manager = UserContextManager()
    agent = CareerPathPlanningAgent(manager)
    
    # Setup context (assuming previous agents ran)
    user_id = "student_001"
    
    manager.update_career_goals(user_id, {
        "interpreted_goal": {
            "role_title": "Backend Developer",
            "required_skills": ["Python", "SQL", "REST APIs"]
        }
    })
    
    manager.update_readiness(user_id, {
        "confidence_score": 0.65,
        "readiness_verdict": "needs_preparation"
    })
    
    manager.update_market_context(user_id, {
        "target_role_analysis": {
            "demand_score": 75,
            "entry_barrier": "medium"
        }
    })
    
    manager.update_student_profile(user_id, {
        "experience_level": "intermediate",
        "technical_skills": {"programming": ["Python"]}
    })
    
    # Generate path
    result = agent.generate_path(user_id=user_id, duration_weeks=12)
    print(json.dumps(result, indent=2))
