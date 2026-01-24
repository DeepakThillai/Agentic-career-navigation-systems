"""
Action & Recommendation Agent
Converts career paths into executable short-term actions
"""

import json
import os
from typing import Dict, Any, List
import requests
from datetime import datetime
from ..user_context import UserContextManager
from ..utils.api_client import APIClient
from ..utils.api_key_manager import get_key_manager


class ActionRecommendationAgent:
    """
    Generates actionable tasks from career paths
    """
    
    AGENT_NAME = "Action & Recommendation Agent"
    AGENT_OBJECTIVE = (
        "Convert the active career path into short-term executable actions. "
        "Prioritize actions based on impact and effort. "
        "Do NOT change the career path."
    )
    
    def __init__(self, context_manager: UserContextManager):
        """Initialize agent"""
        self.context_manager = context_manager
        key_manager = get_key_manager()
        self.api_key = key_manager.get_key_for_agent("ActionRecommendationAgent")
    
    def _call_llm(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Groq LLM with agent-specific prompt"""
        
        output_schema = """{
  "action_plan": {
    "current_focus": "What to focus on right now",
    "priority_actions": [
      {
        "action_id": "action_1",
        "title": "Action Title",
        "description": "Specific task to complete",
        "type": "learning/practice/project/networking/application",
        "estimated_hours": 8,
        "estimated_days": 7,
        "priority": "high/medium/low",
        "impact_score": 9,
        "effort_score": 6,
        "prerequisites": ["completed_action_id"],
        "success_criteria": "How to know it's done",
        "resources": [
          {
            "title": "Resource name",
            "url": "URL or description",
            "type": "course/article/video/tool"
          }
        ],
        "tips": ["tip1", "tip2"]
      }
    ],
    "this_week": ["action_id_1", "action_id_2"],
    "next_week": ["action_id_3", "action_id_4"],
    "this_month": ["action_id_5", "action_id_6"],
    "quick_wins": ["Small achievable task 1", "Small achievable task 2"],
    "daily_habits": ["habit1", "habit2"],
    "progress_indicators": ["indicator1", "indicator2"],
    "motivation_boosters": ["tip1", "tip2"]
  }
}"""
        
        system_prompt = f"""You are an autonomous agent operating inside an Agentic AI–Powered Career Navigation System.

AGENT_NAME: {self.AGENT_NAME}

AGENT_OBJECTIVE: {self.AGENT_OBJECTIVE}

INPUT_JSON:
{json.dumps(input_data, indent=2)}

RESPONSIBILITIES:
- Break down career path steps into concrete, actionable tasks
- Each action should be specific and measurable
- Prioritize by impact vs effort (impact_score / effort_score)
- Provide clear success criteria for each action
- Include resource recommendations
- Do NOT modify the career path itself
- Focus on what student can START DOING TODAY

ACTION CHARACTERISTICS:
- Specific: "Complete Python course module 1-3" not "Learn Python"
- Measurable: Clear success criteria
- Time-bound: Estimated hours/days
- Achievable: Realistic for student's level

PRIORITIZATION:
- High priority: High impact, manageable effort (impact 7-10, effort 3-7)
- Medium priority: Good impact or low effort
- Low priority: Lower impact or high effort

ACTION TYPES:
- learning: Taking courses, reading, tutorials
- practice: Coding challenges, exercises
- project: Building something tangible
- networking: Connecting with professionals
- application: Applying for jobs/internships

IMPACT SCORE (1-10):
- How much this action moves student toward goal
- Consider: skill relevance, market demand, portfolio value

EFFORT SCORE (1-10):
- How much time/energy required
- Consider: complexity, prerequisites, time investment

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
    
    def generate_actions(self, user_id: str) -> Dict[str, Any]:
        """
        Generate actionable tasks from career path
        
        Args:
            user_id: User identifier
            
        Returns:
            Action plan with prioritized tasks
        """
        
        # Load context
        context = self.context_manager.load_context(user_id)
        
        # Check if there's an active path
        if not context["active_path"].get("path_id"):
            return {
                "agent": self.AGENT_NAME,
                "status": "error",
                "message": "No active career path found. Generate path first."
            }
        
        # Prepare input
        input_data = {
            "active_path": context["active_path"],
            "student_profile": context["student_profile"],
            "progress": context["progress"],
            "completed_actions": context["current_actions"].get("completed_actions", []),
            "current_step": context["progress"].get("current_step"),
            "active_stage": context["progress"].get("active_stage", 1)
        }
        
        # Call LLM
        result = self._call_llm(input_data)
        
        # Extract action plan
        action_plan = result["action_plan"]
        
        # Tag actions with current stage
        current_stage = context["progress"].get("active_stage", 1)
        for action in action_plan["priority_actions"]:
            action["stage"] = current_stage
            action["status"] = "pending"
        
        # Update context with pending actions
        self.context_manager.update_actions(user_id, {
            "pending_actions": action_plan["priority_actions"],
            "priority_actions": [
                a["action_id"] for a in action_plan["priority_actions"] 
                if a["priority"] == "high"
            ]
        })
        
        # Log interaction
        self.context_manager.log_agent_interaction(
            user_id,
            self.AGENT_NAME,
            "actions_generated",
            {
                "actions_count": len(action_plan["priority_actions"]),
                "high_priority_count": len([
                    a for a in action_plan["priority_actions"] 
                    if a["priority"] == "high"
                ])
            }
        )
        
        return {
            "agent": self.AGENT_NAME,
            "status": "success",
            "action_plan": action_plan,
            "context_updated": True
        }
    
    def mark_action_complete(self,
                            user_id: str,
                            action_id: str,
                            time_spent_hours: float = None,
                            notes: str = None) -> Dict[str, Any]:
        """
        Mark an action as completed
        
        Args:
            user_id: User identifier
            action_id: Action identifier
            time_spent_hours: Hours spent on action
            notes: Optional completion notes
            
        Returns:
            Updated action status
        """
        
        context = self.context_manager.load_context(user_id)
        
        # Find action in pending
        pending = context["current_actions"].get("pending_actions", [])
        action = next((a for a in pending if a["action_id"] == action_id), None)
        
        if not action:
            return {
                "agent": self.AGENT_NAME,
                "status": "error",
                "message": f"Action {action_id} not found"
            }
        
        # Mark as completed
        completed_action = {
            **action,
            "completed_at": datetime.now().isoformat(),
            "time_spent_hours": time_spent_hours,
            "notes": notes
        }
        
        # Remove from pending
        updated_pending = [a for a in pending if a["action_id"] != action_id]
        
        # Update context
        self.context_manager.update_actions(user_id, {
            "pending_actions": updated_pending,
            "completed_action": completed_action
        })
        
        # Update progress
        self.context_manager.record_progress(user_id, {
            "last_activity": datetime.now().isoformat(),
            "time_spent_hours": context["progress"].get("time_spent_hours", 0) + (time_spent_hours or 0)
        })
        
        return {
            "agent": self.AGENT_NAME,
            "status": "success",
            "message": f"Action {action_id} marked complete",
            "action": completed_action
        }
    
    def generate_validation_questions(self, user_id: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate validation questions to verify action completion.
        Uses ONE API call to generate targeted questions.
        
        Args:
            user_id: User identifier
            action: Action details (title, description, success_criteria)
            
        Returns:
            Questions for user to answer
        """
        print(f"\n🔑 [GENERATE_QUESTIONS] ActionRecommendationAgent → Using API Key #{self.api_key[-1]}")
        
        try:
            prompt = f"""You are evaluating if a student has truly completed this action. Generate exactly 5 validation questions.

ACTION: {action.get('title', 'Unknown')}
DESCRIPTION: {action.get('description', '')}
SUCCESS CRITERIA: {action.get('success_criteria', '')}

Generate 5 questions that verify the student has completed this action:
- Questions should be SHORT and DIRECT (1-2 sentences max)
- Questions should directly test knowledge/completion of the action
- Questions should be answerable by someone who completed the action
- Mix of theory and practical application

Return ONLY a JSON array with NO markdown or extra text:
["Question 1?", "Question 2?", "Question 3?", "Question 4?", "Question 5?"]"""
            
            result = APIClient.call_groq_api(
                api_key=self.api_key,
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": prompt}],
                temperature=0.6,
                max_tokens=800
            )
            
            content = result["choices"][0]["message"]["content"]
            print(f"[DEBUG] LLM Response: {content[:200]}...")
            
            import re
            
            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                try:
                    questions_text = json_match.group()
                    questions = json.loads(questions_text)
                    if isinstance(questions, list) and len(questions) > 0:
                        print(f"✓ Generated {len(questions)} validation questions")
                        return {
                            "status": "success",
                            "questions": questions,
                            "message": f"Generated {len(questions)} questions"
                        }
                except json.JSONDecodeError as je:
                    print(f"JSON parse error: {je}")
            
            # Fallback questions if parsing fails
            print(f"⚠️ Using fallback questions")
            default_questions = [
                f"What is the main objective of this action?",
                f"What did you learn or accomplish?",
                f"How did you know when you succeeded?",
                f"What was the most challenging part?",
                f"What would you improve next time?"
            ]
            return {
                "status": "success",
                "questions": default_questions,
                "message": "Generated default questions"
            }
            
        except Exception as e:
            print(f"❌ Error generating questions: {e}")
            import traceback
            traceback.print_exc()
            
            # Return fallback questions on error
            default_questions = [
                f"What is the main objective of this action?",
                f"What did you learn or accomplish?",
                f"How did you know when you succeeded?",
                f"What was the most challenging part?",
                f"What would you improve next time?"
            ]
            return {
                "status": "success",
                "questions": default_questions,
                "message": "Generated default questions (error occurred)"
            }


# Example usage
if __name__ == "__main__":
    from ..user_context import UserContextManager
    from ..utils.api_client import APIClient
    
    manager = UserContextManager()
    agent = ActionRecommendationAgent(manager)
    
    # Setup context
    user_id = "student_001"
    
    manager.update_active_path(user_id, {
        "path_id": "path-123",
        "target_role": "Backend Developer",
        "primary_path": {
            "steps": [
                {
                    "step_number": 1,
                    "title": "Master Python Fundamentals",
                    "skills_to_learn": ["Python", "OOP"],
                    "duration_weeks": 4
                }
            ]
        }
    })
    
    # Generate actions
    result = agent.generate_actions(user_id=user_id)
    print(json.dumps(result, indent=2))
    
    # Mark action complete
    if result["status"] == "success":
        first_action_id = result["action_plan"]["priority_actions"][0]["action_id"]
        complete_result = agent.mark_action_complete(
            user_id=user_id,
            action_id=first_action_id,
            time_spent_hours=8.5,
            notes="Completed Python basics course"
        )
        print("\nAction completion:")
        print(json.dumps(complete_result, indent=2))
