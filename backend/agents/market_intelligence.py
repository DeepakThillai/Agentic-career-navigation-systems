"""
Market Intelligence Agent
Assesses market demand and feasibility for target roles
"""

import json
import os
from typing import Dict, Any, List
import requests
from ..user_context import UserContextManager
from ..utils.api_client import APIClient
from ..utils.api_key_manager import get_key_manager

class MarketIntelligenceAgent:
    """
    Evaluates market demand, competition, and identifies adjacent roles
    """
    
    AGENT_NAME = "Market Intelligence Agent"
    AGENT_OBJECTIVE = (
        "Assess external feasibility of the target role. "
        "Evaluate entry-level competition and demand. "
        "Identify safer adjacent roles. "
        "Do NOT personalize advice."
    )
    
    def __init__(self, context_manager: UserContextManager):
        """Initialize agent"""
        self.context_manager = context_manager
        key_manager = get_key_manager()
        self.api_key = key_manager.get_key_for_agent("MarketIntelligenceAgent")
    
    def _call_llm(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Groq LLM with agent-specific prompt"""
        
        output_schema = """{
  "market_analysis": {
    "role_title": "Target Role",
    "demand_score": 75,
    "competition_level": "low/medium/high",
    "entry_barrier": "low/medium/high",
    "market_trend": "growing/stable/declining",
    "avg_salary_range_usd": "60k-90k",
    "required_experience_years": "0-2",
    "key_hiring_companies": ["Company1", "Company2"],
    "in_demand_skills": ["skill1", "skill2", "skill3"],
    "market_saturation": "low/medium/high",
    "job_availability": "abundant/moderate/scarce",
    "adjacent_safer_roles": [
      {
        "role": "Role Name",
        "reason": "Why this is safer/easier",
        "demand_score": 80,
        "entry_barrier": "low"
      }
    ],
    "market_notes": "Key insights about this role's market",
    "last_updated": "2026-01-23"
  }
}"""
        
        system_prompt = f"""You are an autonomous agent operating inside an Agentic AI-Powered Career Navigation System.

AGENT_NAME: {self.AGENT_NAME}

AGENT_OBJECTIVE: {self.AGENT_OBJECTIVE}

INPUT_JSON:
{json.dumps(input_data, indent=2)}

RESPONSIBILITIES:
- Assess current market demand for the target role (demand_score 0-100)
- Evaluate competition level and entry barriers
- Identify market trends (growing/stable/declining)
- List in-demand skills employers are looking for
- Identify 2-3 adjacent roles that are easier to enter
- Do NOT consider student profile - this is pure market analysis
- Be realistic and data-driven

DEMAND SCORE:
- 80-100: Very high demand, excellent opportunities
- 60-80: Good demand, competitive
- 40-60: Moderate demand, selective hiring
- 20-40: Low demand, challenging market
- 0-20: Very low demand, limited opportunities

ENTRY BARRIER:
- low: Accessible to entry-level candidates
- medium: Requires some experience or specialization
- high: Requires significant experience or advanced degree

ADJACENT SAFER ROLES:
- Roles with lower entry barriers
- Roles with higher demand
- Roles that use similar skills but less specialized

OUTPUT_SCHEMA:
{output_schema}

Return ONLY valid JSON matching the schema. No markdown, no explanations."""

        try:
            result = APIClient.call_groq_api(
                api_key=self.api_key,
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.4,
                max_tokens=2000
            )
            
            content = result["choices"][0]["message"]["content"]
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
            
        except Exception as e:
            print(f"LLM call error: {e}")
            raise
    
    def analyze_market(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze market conditions for target role
        
        Args:
            user_id: User identifier
            
        Returns:
            Market analysis with demand and competition data
        """
        
        # Load context
        context = self.context_manager.load_context(user_id)
        
        # Check if we have interpreted goal
        if not context["career_goals"].get("interpreted_goal"):
            return {
                "agent": self.AGENT_NAME,
                "status": "error",
                "message": "No interpreted goal found. Run Goal Interpretation Agent first."
            }
        
        # Prepare input (no student profile - pure market analysis)
        input_data = {
            "target_role": context["career_goals"]["interpreted_goal"],
            "analysis_date": "2026-01-23"
        }
        
        # Call LLM
        result = self._call_llm(input_data)
        
        # Extract market analysis
        market_analysis = result["market_analysis"]
        
        # Update context
        self.context_manager.update_market_context(user_id, {
            "target_role_analysis": market_analysis,
            "market_trends": [
                {
                    "role": market_analysis["role_title"],
                    "demand_score": market_analysis["demand_score"],
                    "trend": market_analysis["market_trend"],
                    "timestamp": market_analysis["last_updated"]
                }
            ]
        })
        
        # Log interaction
        self.context_manager.log_agent_interaction(
            user_id,
            self.AGENT_NAME,
            "market_analyzed",
            {
                "role": market_analysis["role_title"],
                "demand_score": market_analysis["demand_score"],
                "trend": market_analysis["market_trend"]
            }
        )
        
        return {
            "agent": self.AGENT_NAME,
            "status": "success",
            "market_analysis": market_analysis,
            "context_updated": True
        }


# Example usage
if __name__ == "__main__":
    from ..user_context import UserContextManager
    
    manager = UserContextManager()
    agent = MarketIntelligenceAgent(manager)
    
    # Setup context
    manager.update_career_goals("student_001", {
        "interpreted_goal": {
            "role_title": "Machine Learning Engineer",
            "required_skills": ["Python", "ML algorithms", "TensorFlow"]
        }
    })
    
    # Analyze market
    result = agent.analyze_market(user_id="student_001")
    print(json.dumps(result, indent=2))
