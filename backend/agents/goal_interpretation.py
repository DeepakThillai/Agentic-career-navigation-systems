"""
Goal Interpretation Agent
Converts vague career aspirations into concrete, well-defined roles
"""

import json
import os
from typing import Dict, Any
import requests
from ..user_context import UserContextManager
from ..utils.api_client import APIClient
from ..utils.api_key_manager import get_key_manager

class GoalInterpretationAgent:
    """
    Converts vague career goals into specific, actionable role definitions
    """
    
    AGENT_NAME = "Goal Interpretation Agent"
    AGENT_OBJECTIVE = (
        "Convert vague aspirations into concrete, well-defined career roles. "
        "Normalize ambiguous or broad goals. "
        "Estimate goal clarity and required commitment."
    )
    
    def __init__(self, context_manager: UserContextManager):
        """Initialize agent"""
        self.context_manager = context_manager
        key_manager = get_key_manager()
        self.api_key = key_manager.get_key_for_agent("GoalInterpretationAgent")
    
    def _call_llm(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Groq LLM with agent-specific prompt"""
        
        output_schema = """{
  "interpreted_goal": {
    "role_title": "Specific Job Title",
    "role_category": "Category (e.g., Software Development, Data Science)",
    "role_description": "Brief description of the role",
    "required_skills": ["skill1", "skill2", "skill3"],
    "typical_requirements": ["requirement1", "requirement2"],
    "typical_responsibilities": ["responsibility1", "responsibility2"],
    "goal_clarity_score": 0.85,
    "commitment_level": "low/medium/high",
    "time_to_competency_months": 6,
    "interpretation_notes": "Why this interpretation was chosen"
  }
}"""
        
        system_prompt = f"""You are an autonomous agent operating inside an Agentic AI–Powered Career Navigation System.

AGENT_NAME: {self.AGENT_NAME}

AGENT_OBJECTIVE: {self.AGENT_OBJECTIVE}

INPUT_JSON:
{json.dumps(input_data, indent=2)}

RESPONSIBILITIES:
- Convert vague or ambiguous career goals into specific role titles
- Normalize broad goals (e.g., "AI" -> "Machine Learning Engineer" or "Data Scientist")
- Estimate how clear the goal is (goal_clarity_score)
- Determine required commitment level
- Do NOT evaluate student fit - only interpret the goal

EXAMPLES:
- "I want to work in AI" -> "Machine Learning Engineer" (medium clarity)
- "Backend development" -> "Backend Software Engineer" (high clarity)
- "Tech" -> "Software Developer" (low clarity, needs more info)

OUTPUT_SCHEMA:
{output_schema}

Return ONLY valid JSON matching the schema. No markdown, no explanations."""

        try:
            result = APIClient.call_groq_api(
                api_key=self.api_key,
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = result["choices"][0]["message"]["content"]
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
            
        except Exception as e:
            print(f"LLM call error: {e}")
            raise
    
    def interpret_goal(self, 
                      user_id: str,
                      desired_role: str) -> Dict[str, Any]:
        """
        Interpret vague career goal into concrete role
        
        Args:
            user_id: User identifier
            desired_role: User's stated career goal (may be vague)
            
        Returns:
            Interpreted goal with clarity assessment
        """
        
        # Load context to understand student background
        context = self.context_manager.load_context(user_id)
        
        # Prepare input
        input_data = {
            "desired_role": desired_role,
            "student_background": {
                "education": context["student_profile"]["personal_info"].get("education"),
                "experience_level": context["student_profile"].get("experience_level"),
                "current_skills": context["student_profile"].get("technical_skills", {})
            },
            "previous_goals": context["career_goals"].get("goal_history", [])
        }
        
        # Call LLM
        result = self._call_llm(input_data)
        
        # Extract interpreted goal
        interpreted_goal = result["interpreted_goal"]
        
        # Update context
        self.context_manager.update_career_goals(user_id, {
            "current_goal": desired_role,
            "interpreted_goal": interpreted_goal,
            "goal_clarity_score": interpreted_goal["goal_clarity_score"],
            "commitment_level": interpreted_goal["commitment_level"]
        })
        
        # Log interaction
        self.context_manager.log_agent_interaction(
            user_id,
            self.AGENT_NAME,
            "goal_interpreted",
            {
                "original_goal": desired_role,
                "interpreted_role": interpreted_goal["role_title"],
                "clarity_score": interpreted_goal["goal_clarity_score"]
            }
        )
        
        return {
            "agent": self.AGENT_NAME,
            "status": "success",
            "interpreted_goal": interpreted_goal,
            "context_updated": True
        }


# Example usage
if __name__ == "__main__":
    from ..user_context import UserContextManager
    
    manager = UserContextManager()
    agent = GoalInterpretationAgent(manager)
    
    # First set up a basic profile
    manager.update_student_profile("student_001", {
        "personal_info": {"education": "B.Tech CS"},
        "experience_level": "intermediate"
    })
    
    # Interpret vague goal
    result = agent.interpret_goal(
        user_id="student_001",
        desired_role="I want to work in AI"
    )
    
    print(json.dumps(result, indent=2))
