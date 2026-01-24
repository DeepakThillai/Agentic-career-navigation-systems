"""
Re-Routing & Failure Detection Agent
Detects path failures and proposes alternative routes
"""

import json
import os
from typing import Dict, Any
import requests
from datetime import datetime
from ..user_context import UserContextManager
from ..utils.api_client import APIClient
from ..utils.api_key_manager import get_key_manager


class ReroutingAgent:
    """
    Detects failures and generates alternative career paths
    """
    
    AGENT_NAME = "Re-Routing & Failure Detection Agent"
    AGENT_OBJECTIVE = (
        "Detect deviation or repeated failure. "
        "Explain why the current path is failing. "
        "Propose adjusted or alternate paths. "
        "Preserve past progress where possible."
    )
    
    def __init__(self, context_manager: UserContextManager):
        """Initialize agent"""
        self.context_manager = context_manager
        key_manager = get_key_manager()
        self.api_key = key_manager.get_key_for_agent("ReroutingAgent")
    
    def _call_llm(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Groq LLM with agent-specific prompt"""
        
        output_schema = """{
  "reroute_analysis": {
    "failure_detected": true,
    "failure_type": "skill_gap/time_constraint/motivation_loss/market_changed",
    "failure_reasons": ["reason1", "reason2"],
    "progress_salvageable": true,
    "salvageable_skills": ["skill1", "skill2"],
    "recommended_action": "adjust_timeline/change_path/take_break/seek_mentor",
    "alternative_paths": [
      {
        "new_target_role": "Alternative Role",
        "why_better_fit": "Explanation",
        "leverages_existing_progress": true,
        "existing_skills_applicable": ["skill1", "skill2"],
        "additional_skills_needed": ["skill3", "skill4"],
        "success_probability": 0.75,
        "estimated_duration_months": 6
      }
    ],
    "adjusted_original_path": {
      "keep_original_goal": true,
      "modifications": ["change1", "change2"],
      "extended_timeline_months": 16,
      "additional_support_needed": ["support1", "support2"]
    },
    "confidence_in_recommendation": 0.80,
    "next_steps": ["step1", "step2", "step3"]
  }
}"""
        
        system_prompt = f"""You are an autonomous agent operating inside an Agentic AI-Powered Career Navigation System.

AGENT_NAME: {self.AGENT_NAME}

AGENT_OBJECTIVE: {self.AGENT_OBJECTIVE}

INPUT_JSON:
{json.dumps(input_data, indent=2)}

RESPONSIBILITIES:
- Detect if student is deviating from path or repeatedly failing
- Analyze WHY the failure is happening
- Determine what progress can be salvaged
- Propose alternative paths that build on existing progress
- Offer path adjustments (extended timeline, different approach)
- Be empathetic - failure is data, not defeat

FAILURE TYPES:
- skill_gap: Student lacks prerequisites
- time_constraint: Not enough time available
- motivation_loss: Losing interest or confidence
- market_changed: Job market shifted
- unrealistic_expectations: Goal was too ambitious

REROUTING PRINCIPLES:
- Preserve as much progress as possible
- Suggest roles that use skills already learned
- Offer both "pivot" and "persist with changes" options
- Be realistic about success probability
- Maintain student's confidence and motivation

ALTERNATIVE PATH CRITERIA:
- Must have higher success probability than current path
- Should leverage existing skills/progress
- Must be market-viable
- Should align with student's strengths

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
    
    def detect_and_reroute(self,
                          user_id: str,
                          failure_evidence: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Detect failure and generate rerouting options
        
        Args:
            user_id: User identifier
            failure_evidence: Optional dict with failure indicators
                             (e.g., {"blockers": 3, "completion_rate": 0.2})
            
        Returns:
            Rerouting analysis with alternatives
        """
        
        # Load context
        context = self.context_manager.load_context(user_id)
        
        # Check if there's an active path
        if not context["active_path"].get("path_id"):
            return {
                "agent": self.AGENT_NAME,
                "status": "error",
                "message": "No active path found. Nothing to reroute."
            }
        
        # Prepare input
        input_data = {
            "current_path": context["active_path"],
            "student_profile": context["student_profile"],
            "progress": context["progress"],
            "readiness": context["readiness"],
            "market_context": context["market_context"],
            "reroute_history": context["reroute_history"],
            "failure_evidence": failure_evidence or {
                "blockers_count": len(context["progress"].get("blockers", [])),
                "completion_rate": context["progress"].get("completion_rate", 0.0),
                "time_spent": context["progress"].get("time_spent_hours", 0)
            }
        }
        
        # Call LLM
        result = self._call_llm(input_data)
        
        # Extract reroute analysis
        reroute_analysis = result["reroute_analysis"]
        
        # Update context with reroute event
        self.context_manager.record_reroute(user_id, {
            "failed_path": {
                "path_id": context["active_path"]["path_id"],
                "target_role": context["active_path"]["target_role"],
                "failure_type": reroute_analysis["failure_type"],
                "timestamp": datetime.now().isoformat()
            },
            "reason": reroute_analysis["failure_reasons"],
            "alternatives": reroute_analysis["alternative_paths"]
        })
        
        # Update active path status
        self.context_manager.update_active_path(user_id, {
            "status": "failed"
        })
        
        # Log interaction
        self.context_manager.log_agent_interaction(
            user_id,
            self.AGENT_NAME,
            "reroute_performed",
            {
                "failure_type": reroute_analysis["failure_type"],
                "alternatives_count": len(reroute_analysis["alternative_paths"]),
                "reroute_number": context["reroute_history"]["reroute_count"] + 1
            }
        )
        
        return {
            "agent": self.AGENT_NAME,
            "status": "success",
            "reroute_analysis": reroute_analysis,
            "context_updated": True
        }


# Example usage
if __name__ == "__main__":
    from ..user_context import UserContextManager
    from ..utils.api_client import APIClient
    
    manager = UserContextManager()
    agent = ReroutingAgent(manager)
    
    # Setup context with failing path
    user_id = "student_001"
    
    manager.update_active_path(user_id, {
        "path_id": "path-123",
        "target_role": "Machine Learning Engineer",
        "status": "in_progress"
    })
    
    manager.record_progress(user_id, {
        "completion_rate": 0.15,
        "time_spent_hours": 40,
        "blocker": {
            "step": 2,
            "reason": "Cannot understand neural networks",
            "timestamp": datetime.now().isoformat()
        }
    })
    
    manager.update_student_profile(user_id, {
        "experience_level": "beginner",
        "technical_skills": {"programming": ["Python"]}
    })
    
    # Detect failure and reroute
    result = agent.detect_and_reroute(
        user_id=user_id,
        failure_evidence={
            "blockers_count": 3,
            "completion_rate": 0.15,
            "repeated_failures": True
        }
    )
    
    print(json.dumps(result, indent=2))
