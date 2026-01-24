"""
Goal Readiness & Confidence Assessment Agent
Generates diagnostic questions and assesses readiness for target role
"""

import json
import os
from typing import Dict, Any, List, Optional
import requests
from ..user_context import UserContextManager
from ..utils.api_client import APIClient
from ..utils.api_key_manager import get_key_manager

class ReadinessAssessmentAgent:
    """
    Generates diagnostic questions and evaluates goal readiness
    """
    
    AGENT_NAME = "Goal Readiness & Confidence Assessment Agent"
    AGENT_OBJECTIVE = (
        "Generate exactly 5 diagnostic questions relevant to the target role. "
        "Evaluate user's answers if provided. "
        "Estimate goal confidence score and deviation risk. "
        "Identify conceptual weak areas. "
        "Do NOT change the goal directly."
    )
    
    def __init__(self, context_manager: UserContextManager):
        """Initialize agent"""
        self.context_manager = context_manager
        key_manager = get_key_manager()
        self.api_key = key_manager.get_key_for_agent("ReadinessAssessmentAgent")
    
    def _call_llm(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Groq LLM with agent-specific prompt"""
        
        output_schema = """{
  "readiness_assessment": {
    "diagnostic_questions": [
      {
        "question_number": 1,
        "question": "Question text here",
        "purpose": "What this question tests",
        "category": "technical/conceptual/practical"
      }
    ],
    "evaluation": {
      "answers_evaluated": true/false,
      "correct_count": 0,
      "weak_areas": ["area1", "area2"],
      "strong_areas": ["area1", "area2"]
    },
    "confidence_score": 0.65,
    "deviation_risk": "low/medium/high",
    "readiness_verdict": "ready/needs_preparation/not_ready",
    "preparation_time_estimate_weeks": 8,
    "key_gaps": ["gap1", "gap2"],
    "assessment_notes": "Overall assessment summary"
  }
}"""
        
        system_prompt = f"""You are an autonomous agent operating inside an Agentic AI-Powered Career Navigation System.

AGENT_NAME: {self.AGENT_NAME}

AGENT_OBJECTIVE: {self.AGENT_OBJECTIVE}

INPUT_JSON:
{json.dumps(input_data, indent=2)}

RESPONSIBILITIES:
- Calculate confidence score (0.0-1.0) based on profile and target role
- Assess deviation risk (likelihood of giving up)
- Identify specific weak areas that need work
- Do NOT change or suggest different goals

{f'''QUESTION GENERATION (ONLY IF GENERATE_QUESTIONS = true):
- Generate EXACTLY 5 diagnostic questions relevant to the target role
- Questions should test: technical knowledge, conceptual understanding, practical awareness
''' if input_data.get('generate_questions') else ''}

{f'''ANSWER EVALUATION (IF ANSWERS PROVIDED):
- Evaluate answers objectively
- Calculate accuracy of responses
''' if input_data.get('answers_provided') else ''}

CONFIDENCE SCORE CALCULATION:
- 0.8-1.0: Strong match, ready to start
- 0.6-0.8: Good potential, needs some prep
- 0.4-0.6: Significant gaps, needs structured learning
- 0.2-0.4: Major mismatch, consider alternatives
- 0.0-0.2: Not feasible with current profile

DEVIATION RISK FACTORS:
- Large skill gaps = higher risk
- Unclear goal understanding = higher risk
- Strong foundation = lower risk
- Relevant experience = lower risk

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
    
    def assess_readiness(self,
                        user_id: str,
                        answers: List[str] = None,
                        generate_questions: bool = False) -> Dict[str, Any]:
        """
        Generate diagnostic questions or evaluate answers
        
        Args:
            user_id: User identifier
            answers: Optional list of answers to diagnostic questions
            generate_questions: Whether to generate questions (default: False)
                               Set to True only during action completion phase
            
        Returns:
            Assessment with questions and/or evaluation
        """
        
        # Load context
        context = self.context_manager.load_context(user_id)
        
        # Check if we have interpreted goal
        interpreted_goal = context.get("career_goals", {}).get("interpreted_goal")
        if not interpreted_goal:
            print(f"⚠️ Warning: No interpreted goal found for {user_id}. Using current goal instead.")
            current_goal = context.get("career_goals", {}).get("current_goal")
            if not current_goal:
                return {
                    "agent": self.AGENT_NAME,
                    "status": "error",
                    "message": "No goal found. Run Goal Interpretation Agent first.",
                    "readiness_assessment": {
                        "readiness_verdict": "not_ready",
                        "confidence_score": 0.0,
                        "deviation_risk": "high",
                        "key_gaps": [],
                        "assessment_notes": "Cannot assess readiness without a career goal"
                    }
                }
            interpreted_goal = current_goal
        
        # Prepare input
        input_data = {
            "target_role": interpreted_goal if isinstance(interpreted_goal, str) else interpreted_goal.get("role_title", "Unknown Role"),
            "student_profile": context["student_profile"],
            "existing_questions": context["readiness"].get("diagnostic_questions", []) if generate_questions else [],
            "answers_provided": answers if answers else None,
            "generate_questions": generate_questions
        }
        
        # Call LLM
        try:
            result = self._call_llm(input_data)
        except Exception as e:
            print(f"❌ Error calling LLM in readiness assessment: {e}")
            return {
                "agent": self.AGENT_NAME,
                "status": "error",
                "message": f"LLM error: {str(e)}",
                "readiness_assessment": {
                    "readiness_verdict": "needs_preparation",
                    "confidence_score": 0.5,
                    "deviation_risk": "medium",
                    "key_gaps": ["Unable to assess due to technical error"],
                    "assessment_notes": f"Technical error during assessment: {str(e)}"
                }
            }
        
        # Extract assessment
        assessment = result["readiness_assessment"]
        
        # Update context
        readiness_update = {
            "confidence_score": assessment["confidence_score"],
            "deviation_risk": assessment["deviation_risk"],
            "weak_areas": assessment.get("key_gaps", []),
            "readiness_verdict": assessment["readiness_verdict"]
        }
        
        # Only store questions if generation was requested
        if generate_questions:
            readiness_update["diagnostic_questions"] = assessment.get("diagnostic_questions", [])
        
        if answers:
            readiness_update["diagnostic_answers"] = answers
        
        self.context_manager.update_readiness(user_id, readiness_update)
        print(f"✓ Readiness assessment saved to context for {user_id}")
        
        # Log interaction
        self.context_manager.log_agent_interaction(
            user_id,
            self.AGENT_NAME,
            "readiness_assessed" if answers else "readiness_scored",
            {
                "confidence_score": assessment["confidence_score"],
                "readiness": assessment["readiness_verdict"],
                "answers_evaluated": bool(answers),
                "questions_generated": generate_questions
            }
        )
        
        return {
            "agent": self.AGENT_NAME,
            "status": "success",
            "readiness_assessment": assessment,
            "context_updated": True
        }


# Example usage
if __name__ == "__main__":
    from ..user_context import UserContextManager
    
    manager = UserContextManager()
    agent = ReadinessAssessmentAgent(manager)
    
    # Setup context (assuming previous agents ran)
    manager.update_career_goals("student_001", {
        "interpreted_goal": {
            "role_title": "Machine Learning Engineer",
            "required_skills": ["Python", "ML algorithms", "TensorFlow"]
        }
    })
    
    manager.update_student_profile("student_001", {
        "experience_level": "intermediate",
        "technical_skills": {
            "programming": ["Python", "Java"]
        }
    })
    
    # Generate questions
    result = agent.assess_readiness(user_id="student_001")
    print(json.dumps(result, indent=2))
    
    # Later, evaluate with answers
    answers = [
        "Supervised learning uses labeled data",
        "TensorFlow is a framework",
        "Not sure about gradient descent",
        "Neural networks have layers",
        "I don't know about deployment"
    ]
    
    result = agent.assess_readiness(user_id="student_001", answers=answers)
    print("\nWith answers:")
    print(json.dumps(result, indent=2))
