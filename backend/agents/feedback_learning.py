"""
Feedback & Learning Agent
Evaluates action effectiveness and updates confidence signals
"""

import json
import os
from typing import Dict, Any, List
import requests
from datetime import datetime
from ..user_context import UserContextManager
from ..utils.api_client import APIClient
from ..utils.api_key_manager import get_key_manager


class FeedbackLearningAgent:
    """
    Analyzes progress and provides feedback for continuous improvement
    """
    
    AGENT_NAME = "Feedback & Learning Agent"
    AGENT_OBJECTIVE = (
        "Evaluate effectiveness of prior actions. "
        "Update confidence and risk signals. "
        "Provide feedback for future planning."
    )
    
    def __init__(self, context_manager: UserContextManager):
        """Initialize agent"""
        self.context_manager = context_manager
        key_manager = get_key_manager()
        self.api_key = key_manager.get_key_for_agent("FeedbackLearningAgent")
    
    def _call_llm(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Groq LLM with agent-specific prompt"""
        
        output_schema = """{
  "feedback_analysis": {
    "overall_progress_rating": "excellent/good/fair/poor",
    "progress_percentage": 45,
    "velocity_assessment": "ahead_of_schedule/on_track/behind_schedule/stalled",
    "confidence_adjustment": 0.05,
    "updated_confidence_score": 0.70,
    "risk_adjustment": "increased/stable/decreased",
    "updated_deviation_risk": "low/medium/high",
    "strengths_observed": ["strength1", "strength2"],
    "areas_of_concern": ["concern1", "concern2"],
    "learning_insights": [
      {
        "insight": "Key observation",
        "evidence": "What shows this",
        "recommendation": "What to do about it"
      }
    ],
    "action_effectiveness": [
      {
        "action_id": "action_1",
        "effectiveness": "high/medium/low",
        "time_efficiency": "faster_than_expected/as_expected/slower_than_expected",
        "impact_on_goal": "Measurable impact",
        "lessons_learned": ["lesson1", "lesson2"]
      }
    ],
    "motivation_level": "high/moderate/low/critical",
    "recommended_adjustments": [
      {
        "adjustment_type": "pace/difficulty/approach/support",
        "reason": "Why this adjustment",
        "specific_change": "What to change"
      }
    ],
    "next_checkpoint_date": "2026-02-15",
    "encouragement_message": "Personalized motivational message"
  }
}"""
        
        system_prompt = f"""You are an autonomous agent operating inside an Agentic AI–Powered Career Navigation System.

AGENT_NAME: {self.AGENT_NAME}

AGENT_OBJECTIVE: {self.AGENT_OBJECTIVE}

INPUT_JSON:
{json.dumps(input_data, indent=2)}

RESPONSIBILITIES:
- Evaluate progress objectively based on completed actions
- Assess action effectiveness (did they help?)
- Update confidence and risk scores based on actual performance
- Identify patterns in learning velocity
- Provide constructive, motivating feedback
- Recommend adjustments to improve outcomes

CONFIDENCE SCORE UPDATES:
- Increase (+0.05 to +0.15): Consistent progress, actions working
- Maintain (0): On track, no major changes
- Decrease (-0.05 to -0.15): Struggling, repeated blockers

RISK ASSESSMENT:
- decreased: Student showing resilience, overcoming challenges
- stable: Normal progress with expected difficulties
- increased: Multiple blockers, slowing down, losing motivation

VELOCITY ASSESSMENT:
- ahead_of_schedule: Completing actions faster than estimated
- on_track: Meeting expectations
- behind_schedule: Taking longer but still progressing
- stalled: Little to no progress for extended period

EFFECTIVENESS EVALUATION:
Consider:
- Time spent vs. time estimated
- Quality of completion
- Impact on next steps
- Student's reported experience

FEEDBACK PRINCIPLES:
- Be honest but encouraging
- Celebrate small wins
- Reframe setbacks as learning opportunities
- Provide specific, actionable recommendations
- Maintain motivation and momentum

OUTPUT_SCHEMA:
{output_schema}

Return ONLY valid JSON matching the schema. No markdown, no explanations."""

        try:
            result = APIClient.call_groq_api(
                api_key=self.api_key,
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.5,
                max_tokens=2500
            )
            
            content = result["choices"][0]["message"]["content"]
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
            
        except Exception as e:
            print(f"LLM call error: {e}")
            raise
    
    def evaluate_progress(self, user_id: str) -> Dict[str, Any]:
        """
        Evaluate overall progress and provide feedback
        
        Args:
            user_id: User identifier
            
        Returns:
            Comprehensive feedback analysis
        """
        
        # Load context
        context = self.context_manager.load_context(user_id)
        
        # Check if there's enough data to evaluate
        if not context["current_actions"].get("completed_actions"):
            return {
                "agent": self.AGENT_NAME,
                "status": "info",
                "message": "No completed actions yet. Complete some actions first."
            }
        
        # Prepare input
        input_data = {
            "student_profile": context["student_profile"],
            "active_path": context["active_path"],
            "progress": context["progress"],
            "completed_actions": context["current_actions"]["completed_actions"],
            "pending_actions": context["current_actions"].get("pending_actions", []),
            "current_readiness": context["readiness"],
            "reroute_history": context["reroute_history"]
        }
        
        # Call LLM
        result = self._call_llm(input_data)
        
        # Extract feedback
        feedback = result["feedback_analysis"]
        
        # Update readiness scores based on feedback
        self.context_manager.update_readiness(user_id, {
            "confidence_score": feedback["updated_confidence_score"],
            "deviation_risk": feedback["updated_deviation_risk"]
        })
        
        # Update progress metrics
        self.context_manager.record_progress(user_id, {
            "completion_rate": feedback["progress_percentage"] / 100.0,
            "last_activity": datetime.now().isoformat()
        })
        
        # Log interaction
        self.context_manager.log_agent_interaction(
            user_id,
            self.AGENT_NAME,
            "feedback_generated",
            {
                "progress_rating": feedback["overall_progress_rating"],
                "velocity": feedback["velocity_assessment"],
                "confidence_change": feedback["confidence_adjustment"]
            }
        )
        
        return {
            "agent": self.AGENT_NAME,
            "status": "success",
            "feedback_analysis": feedback,
            "context_updated": True
        }
    
    def record_blocker(self,
                      user_id: str,
                      action_id: str,
                      blocker_description: str,
                      attempted_solutions: List[str] = None) -> Dict[str, Any]:
        """
        Record a blocker/obstacle encountered
        
        Args:
            user_id: User identifier
            action_id: Action where blocker occurred
            blocker_description: Description of the blocker
            attempted_solutions: What student tried to resolve it
            
        Returns:
            Blocker acknowledgment and guidance
        """
        
        blocker_entry = {
            "action_id": action_id,
            "description": blocker_description,
            "attempted_solutions": attempted_solutions or [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Record in context
        self.context_manager.record_progress(user_id, {
            "blocker": blocker_entry
        })
        
        # Log interaction
        self.context_manager.log_agent_interaction(
            user_id,
            self.AGENT_NAME,
            "blocker_recorded",
            {
                "action_id": action_id,
                "blocker_count": len(self.context_manager.load_context(user_id)["progress"]["blockers"])
            }
        )
        
        return {
            "agent": self.AGENT_NAME,
            "status": "success",
            "message": "Blocker recorded. Consider reaching out for help or reviewing prerequisites.",
            "blocker": blocker_entry
        }
    
    def evaluate_action_answers(self, user_id: str, action: Dict[str, Any], answers: List[str]) -> Dict[str, Any]:
        """
        Evaluate student's answers to action validation questions.
        Uses ONE API call to assess completion quality.
        
        Args:
            user_id: User identifier
            action: Action details (title, success_criteria, questions)
            answers: Student's answers to questions
            
        Returns:
            Evaluation with relevance_score (0-1) and feedback
        """
        print(f"\n🔑 [EVALUATE_ANSWERS] FeedbackLearningAgent → Using API Key #{self.api_key[-1]}")
        
        try:
            # Format questions and answers for evaluation
            questions_text = "\n".join([
                f"Q{i+1}: {q}" 
                for i, q in enumerate(action.get("questions", []))
            ])
            answers_text = "\n".join([
                f"A{i+1}: {a}" 
                for i, a in enumerate(answers)
            ])
            
            prompt = f"""Evaluate if the student truly completed this action based on their answers.

ACTION: {action.get('title', 'Unknown')}
SUCCESS CRITERIA: {action.get('success_criteria', '')}

QUESTIONS ASKED:
{questions_text}

STUDENT ANSWERS:
{answers_text}

Assess:
1. Do answers show real completion? (Yes/No/Partial)
2. Quality of understanding (0-100%)
3. Confidence level in responses

Score from 0.0 to 1.0:
- 0.0-0.3 = Incomplete/Incorrect
- 0.4-0.6 = Partial understanding
- 0.7-1.0 = Strong understanding/Completion

Return ONLY JSON (no markdown):
{{
  "relevance_score": 0.85,
  "agent_satisfied": true,
  "feedback": "Brief feedback on their answers",
  "next_steps": "What to do if not satisfied"
}}"""
            
            result = APIClient.call_groq_api(
                api_key=self.api_key,
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.6,
                max_tokens=500
            )
            
            content = result["choices"][0]["message"]["content"]
            print(f"[DEBUG] Evaluation Response: {content[:200]}...")
            
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    evaluation = json.loads(json_match.group())
                    score = evaluation.get("relevance_score", 0)
                    
                    # Threshold: >= 0.5 = satisfied (50% passing)
                    evaluation["agent_satisfied"] = score >= 0.5
                    
                    print(f"✓ Evaluated answers: Score {score:.2f}, Satisfied: {evaluation['agent_satisfied']}")
                    return evaluation
                except json.JSONDecodeError as je:
                    print(f"JSON parse error: {je}")
            
            # Fallback evaluation
            print(f"⚠️ Using fallback evaluation")
            return {
                "relevance_score": 0.5,
                "agent_satisfied": False,
                "feedback": "Could not evaluate properly. Please try again.",
                "next_steps": "Review success criteria and try answering again"
            }
            
        except Exception as e:
            print(f"❌ Error evaluating answers: {e}")
            import traceback
            traceback.print_exc()
            
            # Return safe fallback on error
            return {
                "relevance_score": 0.0,
                "agent_satisfied": False,
                "feedback": f"Evaluation error: {str(e)}",
                "next_steps": "Please try again later"
            }


# Example usage
if __name__ == "__main__":
    from ..user_context import UserContextManager
    from ..utils.api_client import APIClient
    
    manager = UserContextManager()
    agent = FeedbackLearningAgent(manager)
    
    # Setup context with some progress
    user_id = "student_001"
    
    manager.update_active_path(user_id, {
        "path_id": "path-123",
        "target_role": "Backend Developer"
    })
    
    manager.update_actions(user_id, {
        "completed_actions": [
            {
                "action_id": "action_1",
                "title": "Complete Python basics",
                "estimated_hours": 10,
                "time_spent_hours": 8,
                "completed_at": "2026-01-20T10:00:00"
            },
            {
                "action_id": "action_2",
                "title": "Build simple REST API",
                "estimated_hours": 15,
                "time_spent_hours": 20,
                "completed_at": "2026-01-22T15:00:00"
            }
        ]
    })
    
    manager.update_readiness(user_id, {
        "confidence_score": 0.65,
        "deviation_risk": "medium"
    })
    
    # Evaluate progress
    result = agent.evaluate_progress(user_id=user_id)
    print(json.dumps(result, indent=2))
    
    # Record a blocker
    blocker_result = agent.record_blocker(
        user_id=user_id,
        action_id="action_3",
        blocker_description="Struggling with database design concepts",
        attempted_solutions=["Watched YouTube tutorials", "Read documentation"]
    )
    print("\nBlocker recorded:")
    print(json.dumps(blocker_result, indent=2))
