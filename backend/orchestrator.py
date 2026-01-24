"""
Orchestration Agent (Meta-Agent)
Coordinates all agents and manages workflow
"""

import json
import os
import requests
import time
from typing import Dict, Any, List
from datetime import datetime

from .user_context import UserContextManager
from .utils.api_key_manager import get_key_manager
from .agents.student_profiling import StudentProfilingAgent
from .agents.goal_interpretation import GoalInterpretationAgent
from .agents.readiness_assessment import ReadinessAssessmentAgent
from .agents.market_intelligence import MarketIntelligenceAgent
from .agents.career_path_planning import CareerPathPlanningAgent
from .agents.rerouting import ReroutingAgent
from .agents.action_recommendation import ActionRecommendationAgent
from .agents.feedback_learning import FeedbackLearningAgent


class Orchestrator:
    """
    Meta-agent that coordinates all other agents
    Decides which agents to run based on system events
    """
    
    AGENT_NAME = "Orchestration Agent (Meta-Agent)"
    
    def __init__(self, context_dir: str = None):
        """
        Initialize orchestrator with all agents
        
        Args:
            context_dir: Directory for user context storage
        """
        self.context_manager = UserContextManager(context_dir)
        
        # Get key manager for API key distribution
        self.key_manager = get_key_manager()
        self.api_key = self.key_manager.get_next_key()
        
        print(f"\n✓ API Key Manager initialized with {self.key_manager.get_key_count()} key(s)")
        
        # Initialize all agents
        self.profiling_agent = StudentProfilingAgent(self.context_manager)
        self.goal_agent = GoalInterpretationAgent(self.context_manager)
        self.readiness_agent = ReadinessAssessmentAgent(self.context_manager)
        self.market_agent = MarketIntelligenceAgent(self.context_manager)
        self.path_agent = CareerPathPlanningAgent(self.context_manager)
        self.reroute_agent = ReroutingAgent(self.context_manager)
        self.action_agent = ActionRecommendationAgent(self.context_manager)
        self.feedback_agent = FeedbackLearningAgent(self.context_manager)
        
        # Rate limiting tracking
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
        
        print(f"Orchestrator initialized with all 8 agents")
    
    def _call_llm_with_retry(self, prompt: str, max_tokens: int = 2000, retries: int = 5) -> str:
        """
        Call LLM with retry logic for rate limiting and throttling
        
        Args:
            prompt: The prompt to send
            max_tokens: Maximum tokens in response
            retries: Number of retries on rate limit
            
        Returns:
            Content from LLM response
        """
        # Throttle requests to avoid rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            sleep_time = self.min_request_interval - elapsed
            time.sleep(sleep_time)
        
        for attempt in range(retries):
            try:
                # Update last request time before making request
                self.last_request_time = time.time()
                
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": max_tokens
                    },
                    timeout=30
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Too Many Requests
                    if attempt < retries - 1:
                        wait_time = 2 ** (attempt + 2)  # Exponential backoff: 4, 8, 16, 32, 64 seconds
                        print(f"Rate limited. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{retries})")
                        time.sleep(wait_time)
                    else:
                        raise Exception(f"Rate limited after {retries} retries. API quota may be exhausted.")
                else:
                    raise
            except Exception as e:
                if attempt < retries - 1:
                    print(f"Error: {e}. Retrying... (Attempt {attempt + 1}/{retries})")
                    time.sleep(3)
                else:
                    raise
        
        raise Exception("Failed to get LLM response after all retries")
    
    def _log_api_usage(self, stage: str, agent_name: str, key_number: int = None) -> None:
        """
        Log which API key is being used for tracking purposes
        
        Args:
            stage: Current workflow stage
            agent_name: Name of the agent
            key_number: API key number (1, 2, or 3)
        """
        if key_number is None:
            # Find which key this agent is using
            try:
                key = self.key_manager.get_key_for_agent(agent_name)
                key_list = list(self.key_manager.keys)
                key_number = key_list.index(key) + 1
            except:
                key_number = "?"
        
        print(f"\n🔑 [{stage}] {agent_name} → Using API Key #{key_number}")
    
    def onboard_student(self,
                       user_id: str,
                       desired_role: str,
                       skills: str = None,
                       education: str = None,
                       experience: str = None,
                       projects: List[str] = None,
                       duration_weeks: int = 12) -> Dict[str, Any]:
        """Complete onboarding workflow for new student"""
        
        print(f"\n{'='*70}")
        print(f"ONBOARDING STUDENT: {user_id}")
        print(f"{'='*70}\n")
        
        results = {
            "user_id": user_id,
            "onboarding_timestamp": datetime.now().isoformat(),
            "agent_outputs": {}
        }
        
        try:
            print("[1/6] Running Student Profiling Agent...")
            self._log_api_usage("ONBOARDING", "StudentProfilingAgent", 1)
            profile_result = self.profiling_agent.analyze_profile(
                user_id=user_id,
                skills_text=skills,
                education=education,
                experience=experience,
                projects=projects
            )
            results["agent_outputs"]["profiling"] = profile_result
            print(f"✓ Profile created: {profile_result['student_profile']['experience_level']} level")
            time.sleep(5)  # Increased delay between agents
            
            print("\n[2/6] Running Goal Interpretation Agent...")
            self._log_api_usage("ONBOARDING", "GoalInterpretationAgent", 2)
            goal_result = self.goal_agent.interpret_goal(
                user_id=user_id,
                desired_role=desired_role
            )
            results["agent_outputs"]["goal_interpretation"] = goal_result
            interpreted = goal_result["interpreted_goal"]["role_title"]
            print(f"✓ Goal interpreted: '{desired_role}' -> '{interpreted}'")
            time.sleep(5)
            
            print("\n[3/6] Running Readiness Assessment Agent...")
            self._log_api_usage("ONBOARDING", "ReadinessAssessmentAgent", 3)
            readiness_result = self.readiness_agent.assess_readiness(
                user_id=user_id,
                generate_questions=True  # Generate diagnostic questions during onboarding
            )
            results["agent_outputs"]["readiness"] = readiness_result
            
            # Extract readiness verdict - handle both success and error responses
            if readiness_result.get("status") == "success":
                readiness_data = readiness_result.get("readiness_assessment", {})
                verdict = readiness_data.get("readiness_verdict", "Unknown")
                confidence = readiness_data.get("confidence_score", 0.0)
            else:
                # If agent returned error/warning, use defaults from the response
                readiness_data = readiness_result.get("readiness_assessment", {})
                verdict = readiness_data.get("readiness_verdict", "needs_preparation")
                confidence = readiness_data.get("confidence_score", 0.5)
            
            print(f"✓ Readiness: {verdict}")
            print(f"   Confidence Score: {confidence:.2f}")
            time.sleep(5)
            
            print("\n[4/6] Running Market Intelligence Agent...")
            self._log_api_usage("ONBOARDING", "MarketIntelligenceAgent", 1)
            market_result = self.market_agent.analyze_market(user_id=user_id)
            results["agent_outputs"]["market"] = market_result
            demand = market_result["market_analysis"]["demand_score"]
            print(f"✓ Market demand score: {demand}/100")
            time.sleep(5)
            
            print("\n[5/6] Running Career Path Planning Agent...")
            self._log_api_usage("ROADMAP_GENERATION", "CareerPathPlanningAgent", 2)
            path_result = self.path_agent.generate_path(
                user_id=user_id,
                duration_weeks=duration_weeks
            )
            results["agent_outputs"]["career_path"] = path_result
            success_prob = path_result["career_path"]["success_probability"]
            steps = len(path_result["career_path"]["primary_path"]["steps"])
            print(f"✓ Path generated: {steps} steps, {success_prob*100:.0f}% success probability")
            
            # Save roadmap with steps and actions
            roadmap_data = {
                "roadmap_id": path_result["career_path"]["path_id"],
                "total_steps": steps,
                "steps": path_result["career_path"]["primary_path"]["steps"],
                "current_step_number": 1,
                "completed_steps": [],
                "created_at": datetime.now().isoformat(),
                "status": "generated"
            }
            self.context_manager.update_roadmap(user_id, roadmap_data)
            print(f"✓ Roadmap saved to context with {steps} steps")
            
            time.sleep(5)
            
            print("\n[6/6] Running Action Recommendation Agent...")
            self._log_api_usage("ACTION_GENERATION", "ActionRecommendationAgent", 1)
            action_result = self.action_agent.generate_actions(user_id=user_id)
            results["agent_outputs"]["actions"] = action_result
            actions_count = len(action_result["action_plan"]["priority_actions"])
            print(f"✓ Generated {actions_count} actionable tasks")
            
            print(f"\n{'='*70}")
            print("ONBOARDING COMPLETE!")
            print(f"{'='*70}\n")
            
            results["status"] = "success"
            results["summary"] = {
                "target_role": interpreted,
                "readiness": verdict,
                "market_demand": demand,
                "success_probability": success_prob,
                "path_duration_weeks": path_result["career_path"]["estimated_duration_months"] * 4,
                "immediate_actions": actions_count
            }
            
            return results
            
        except Exception as e:
            print(f"\nError during onboarding: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            return results
    
    def evaluate_and_feedback(self, user_id: str) -> Dict[str, Any]:
        """Run feedback evaluation on student progress"""
        print(f"\nEvaluating progress for {user_id}...")
        result = self.feedback_agent.evaluate_progress(user_id=user_id)
        if result["status"] == "success":
            feedback = result["feedback_analysis"]
            print(f"Progress: {feedback['overall_progress_rating']}")
            print(f"   Velocity: {feedback['velocity_assessment']}")
            print(f"   Confidence: {feedback['updated_confidence_score']}")
        return result
    
    def handle_failure_and_reroute(self, user_id: str, failure_evidence: Dict = None) -> Dict[str, Any]:
        """Detect failure and reroute student"""
        print(f"\nDetecting failures and rerouting for {user_id}...")
        reroute_result = self.reroute_agent.detect_and_reroute(
            user_id=user_id,
            failure_evidence=failure_evidence
        )
        if reroute_result["status"] == "success":
            analysis = reroute_result["reroute_analysis"]
            print(f"Failure detected: {analysis['failure_type']}")
            print(f"   Alternatives found: {len(analysis['alternative_paths'])}")
        return reroute_result
    
    def answer_diagnostic_questions(self, user_id: str, answers: List[str]) -> Dict[str, Any]:
        """Evaluate diagnostic question answers"""
        print(f"\nEvaluating diagnostic answers for {user_id}...")
        result = self.readiness_agent.assess_readiness(user_id=user_id, answers=answers)
        if result["status"] == "success":
            assessment = result["readiness_assessment"]
            print(f"Updated confidence: {assessment['confidence_score']}")
            print(f"   Readiness: {assessment['readiness_verdict']}")
        return result
    
    def complete_action(self, user_id: str, action_id: str, time_spent_hours: float = None, notes: str = None) -> Dict[str, Any]:
        """Mark action as complete and generate validation questions"""
        try:
            # First load context and find the action
            context = self.context_manager.load_context(user_id)
            completed_action = None
            
            # Search in both pending and completed actions
            all_actions = context["current_actions"].get("pending_actions", []) + context["current_actions"].get("completed_actions", [])
            
            for action in all_actions:
                if action.get("title") == action_id or action.get("id") == action_id or action.get("action_id") == action_id:
                    completed_action = action
                    break
            
            if not completed_action:
                return {"status": "error", "message": f"Action '{action_id}' not found"}
            
            # Mark action as in_progress for this attempt
            completed_action["status"] = "in_progress"
            completed_action["attempts"] = completed_action.get("attempts", 0) + 1
            
            # Generate validation questions for this action
            validation_questions = self._generate_action_validation_questions(
                user_id,
                completed_action
            )
            
            # Store questions in context with the action title as key
            if "action_validations" not in context:
                context["action_validations"] = {}
            context["action_validations"][action_id] = {
                "questions": validation_questions,
                "generated_at": datetime.now().isoformat(),
                "status": "pending"
            }
            self.context_manager.save_context(user_id, context)
            
            return {
                "status": "success",
                "validation_questions": validation_questions,
                "message": f"Generated {len(validation_questions)} validation questions"
            }
        
        except Exception as e:
            print(f"Error in complete_action: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    def _generate_action_validation_questions(self, user_id: str, action: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate validation questions for a completed action"""
        context = self.context_manager.load_context(user_id)
        
        prompt = f"""Generate 3 validation questions to test if the student has truly mastered the action:
        
Action: {action.get('title', 'Unknown')}
Description: {action.get('description', '')}
Success Criteria: {action.get('success_criteria', '')}
Target Role: {context['active_path'].get('target_role', 'Unknown')}

Generate exactly 3 questions that:
1. Test conceptual understanding
2. Test practical application
3. Test real-world relevance

Return as JSON array with fields: question, expected_understanding"""
        
        try:
            api_key = os.getenv('GROQ_API_KEY') or "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"
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 1000
                }
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            
            # Parse JSON from response
            import re
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                questions = json.loads(json_match.group())
                if questions and len(questions) > 0:
                    return questions
                    
            # Fallback: Generate basic questions if API parsing fails
            print(f"⚠️ Could not parse API response, using fallback questions")
            return self._get_fallback_validation_questions(action)
            
        except Exception as e:
            print(f"Error generating validation questions: {e}")
            # Return fallback questions on any error
            return self._get_fallback_validation_questions(action)
    
    def _get_fallback_validation_questions(self, action: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fallback validation questions when API fails"""
        action_title = action.get('title', 'Action')
        action_desc = action.get('description', 'Complete this action')
        
        return [
            {"question": f"What is the main objective of '{action_title}'?", "expected_understanding": "Student understands the goal"},
            {"question": f"How does '{action_title}' relate to your career goal?", "expected_understanding": "Student can connect to their path"},
            {"question": f"What did you learn from completing '{action_title}'?", "expected_understanding": "Student reflects on learning"}
        ]
    
    def validate_action_completion(self, user_id: str, action_id: str, answers: List[str]) -> Dict[str, Any]:
        """Evaluate answers to validation questions with score threshold"""
        context = self.context_manager.load_context(user_id)
        
        # Try exact match first
        if action_id not in context.get("action_validations", {}):
            # Try case-insensitive match
            search_key = None
            for key in context.get("action_validations", {}).keys():
                if key.lower() == action_id.lower():
                    search_key = key
                    break
            if not search_key:
                return {"status": "error", "message": f"No validation questions found for action '{action_id}'"}
            action_id = search_key
            return {"status": "error", "message": "No validation questions found for this action"}
        
        validation_data = context["action_validations"][action_id]
        questions = validation_data["questions"]
        
        prompt = f"""Evaluate these answers to validation questions:

Questions and Answers:
"""
        for i, (q, a) in enumerate(zip(questions, answers)):
            prompt += f"\nQ{i+1}: {q.get('question', '')}\nAnswer: {a}"
        
        prompt += f"""

Score EACH answer individually (0-3 scale):
- 0: No understanding or incorrect
- 1: Minimal understanding
- 2: Good understanding  
- 3: Excellent understanding

Calculate total_score by summing individual scores (0-9 scale).

COMPLETION CRITERIA:
- Total score >= 6: Action is COMPLETE - ready_to_proceed = true
- Total score < 6: Action needs REVIEW - ready_to_proceed = false

Return ONLY JSON:
{{
  "individual_scores": [score1, score2, score3],
  "total_score": 7,
  "ready_to_proceed": true,
  "areas_of_strength": ["area1", "area2"],
  "areas_for_improvement": ["area1"],
  "feedback": "What they did well",
  "recommendation": "What to do next or which part to review"
}}"""
        
        try:
            api_key = os.getenv('GROQ_API_KEY') or "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"
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "max_tokens": 800
                }
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                evaluation = json.loads(json_match.group())
                
                # Update context with validation result
                context["action_validations"][action_id]["status"] = "completed"
                context["action_validations"][action_id]["evaluation"] = evaluation
                context["action_validations"][action_id]["answers"] = answers
                context["action_validations"][action_id]["evaluated_at"] = datetime.now().isoformat()
                
                # If score >= 6, move action from pending to completed
                if evaluation.get("total_score", 0) >= 6:
                    pending_actions = context["current_actions"].get("pending_actions", [])
                    completed_actions = context["current_actions"].get("completed_actions", [])
                    
                    # Find and move action
                    search_id = str(action_id).strip().lower()
                    action_index = -1
                    
                    for i, action in enumerate(pending_actions):
                        if action.get("title", "").strip().lower() == search_id:
                            action_index = i
                            break
                    
                    if action_index >= 0:
                        action_to_move = pending_actions.pop(action_index)
                        action_to_move["status"] = "completed"
                        action_to_move["completion_timestamp"] = datetime.now().isoformat()
                        action_to_move["relevance_score"] = evaluation.get("total_score", 0) / 9.0
                        action_to_move["agent_satisfied"] = True
                        action_to_move["user_answers"] = answers
                        
                        completed_actions.append(action_to_move)
                        context["current_actions"]["pending_actions"] = pending_actions
                        context["current_actions"]["completed_actions"] = completed_actions
                        
                        self.context_manager.save_context(user_id, context)
                        self._allocate_next_action(user_id, context)
                        self._check_stage_progression(user_id, context)
                        self.context_manager.save_context(user_id, context)
                else:
                    print(f"⏸️ Action needs review - score {evaluation.get('total_score')}/9 (need 6+)")
                    context["action_validations"][action_id]["retry_suggested"] = True
                    
                    # Mark attempts in pending action
                    all_actions = context["current_actions"].get("pending_actions", [])
                    for action in all_actions:
                        if action.get("title") == action_id or action.get("id") == action_id or action.get("action_id") == action_id:
                            action["attempts"] = action.get("attempts", 0) + 1
                            break
                    
                    # Save for failed validation
                    self.context_manager.save_context(user_id, context)
                    print(f"✅ Context saved for retry attempt")
                
                return {
                    "status": "success",
                    "evaluation": evaluation,
                    "ready_to_proceed": evaluation.get("ready_to_proceed", False),
                    "score": evaluation.get("total_score", 0),
                    "passing_threshold": 6
                }
            return {"status": "error", "message": "Failed to parse evaluation"}
        except Exception as e:
            print(f"Error validating action: {e}")
            return {"status": "error", "message": str(e)}

    def mark_action_as_completed(self, user_id: str, action_id: str, score: int = 9, time_spent_hours: float = 1.0) -> Dict[str, Any]:
        print(f"[DEBUG] mark_action_as_completed called for user_id={user_id}, action_id={action_id}, score={score}, time_spent={time_spent_hours}h")
        """Force-mark an action as completed without running evaluation.

        This is used when the frontend should immediately mark the action complete
        after the user submits the validation form (no LLM evaluation required).
        Returns a success dict with a synthetic evaluation containing the score.
        """
        try:
            context = self.context_manager.load_context(user_id)

            pending_actions = context.get("current_actions", {}).get("pending_actions", [])
            completed_actions = context.get("current_actions", {}).get("completed_actions", [])

            search_id = str(action_id).strip().lower()
            action_index = -1
            for i, action in enumerate(pending_actions):
                if action.get("title", "").strip().lower() == search_id:
                    action_index = i
                    break

            if action_index < 0:
                return {"status": "error", "message": f"Action '{action_id}' not found in pending actions"}

            action_to_move = pending_actions.pop(action_index)
            action_to_move["status"] = "completed"
            action_to_move["completion_timestamp"] = datetime.now().isoformat()
            action_to_move["relevance_score"] = float(score) / 9.0
            action_to_move["agent_satisfied"] = True
            action_to_move["user_answers"] = []
            action_to_move["time_spent_hours"] = time_spent_hours

            completed_actions.append(action_to_move)

            # update context and save
            context["current_actions"]["pending_actions"] = pending_actions
            context["current_actions"]["completed_actions"] = completed_actions
            
            # Update progress metrics
            progress = context.get("progress", {})
            progress["time_spent_hours"] = progress.get("time_spent_hours", 0.0) + time_spent_hours
            progress["last_activity"] = datetime.now().isoformat()
            context["progress"] = progress
            
            print(f"[DEBUG] Saving context after moving action. Pending: {len(pending_actions)}, Completed: {len(completed_actions)}, Total hours: {progress['time_spent_hours']}")
            self.context_manager.save_context(user_id, context)

            # perform stage progression and allocation
            self._allocate_next_action(user_id, context)
            self._check_stage_progression(user_id, context)
            
            # Update overall progress metrics
            completed = context.get("current_actions", {}).get("completed_actions", [])
            pending = context.get("current_actions", {}).get("pending_actions", [])
            total_actions = len(completed) + len(pending)
            if total_actions > 0:
                context["progress"]["completion_rate"] = len(completed) / total_actions
            
            # Update completed_steps in progress object
            if "completed_steps" not in context["progress"]:
                context["progress"]["completed_steps"] = []
            context["progress"]["completed_steps"] = [a.get("title", "") for a in completed]
            
            print(f"[DEBUG] Saving context after allocation/progression. Pending: {len(context['current_actions']['pending_actions'])}, Completed: {len(context['current_actions']['completed_actions'])}")
            print(f"[DEBUG] Progress: {context.get('progress', {})}")
            self.context_manager.save_context(user_id, context)

            evaluation = {
                "individual_scores": [3, 3, 3],
                "total_score": score,
                "ready_to_proceed": True,
                "areas_of_strength": [],
                "areas_for_improvement": [],
                "feedback": "Marked complete by user submission",
                "recommendation": "Proceed to next action"
            }

            return {"status": "success", "evaluation": evaluation, "score": score, "passing_threshold": 6}
        except Exception as e:
            print(f"Error in mark_action_as_completed: {e}")
            return {"status": "error", "message": str(e)}
    
    def _check_stage_progression(self, user_id: str, context: Dict[str, Any]) -> None:
        """Check if current stage is complete and generate next stage if needed"""
        try:
            # Get current stage info
            progress = context.get("progress", {})
            active_stage = progress.get("active_stage", 1)
            
            # Get current stage actions
            pending = context.get("current_actions", {}).get("pending_actions", [])
            completed = context.get("current_actions", {}).get("completed_actions", [])
            
            # Calculate current stage completion rate
            stage_actions = [a for a in completed if a.get("stage") == active_stage]
            total_stage_actions = len([a for a in (completed + pending) if a.get("stage") == active_stage])
            
            if total_stage_actions > 0:
                stage_completion_rate = len(stage_actions) / total_stage_actions
                progress["stage_completion_rate"] = stage_completion_rate
                context["progress"] = progress  # Save progress back to context
                
                print(f"[DEBUG] Stage {active_stage} completion rate: {stage_completion_rate:.1%} ({len(stage_actions)}/{total_stage_actions})")
                
                # If stage is 100% complete and all validated
                if stage_completion_rate >= 1.0:
                    all_validated = all(
                        context.get("action_validations", {}).get(a.get("title"), {}).get("evaluation", {}).get("total_score", 0) >= 6
                        for a in stage_actions
                    )
                    
                    if all_validated:
                        print(f"Stage {active_stage} COMPLETE! Moving to Stage {active_stage + 1}...")
                        self._generate_next_stage(user_id, context, active_stage + 1)
                        return
        except Exception as e:
            print(f"Error checking stage progression: {e}")
    
    def _generate_next_stage(self, user_id: str, context: Dict[str, Any], next_stage: int) -> None:
        """Generate actions for the next stage of the roadmap"""
        try:
            progress = context.get("progress", {})
            
            # Move to next stage
            progress["active_stage"] = next_stage
            progress["stage_completion_rate"] = 0.0
            progress["next_stage_generated_at"] = datetime.now().isoformat()
            
            # Get current active path and regenerate actions for next stage
            active_path = context["active_path"]
            current_step = progress.get("current_step", 0)
            
            # Call action agent to generate next stage actions
            print(f"Generating Stage {next_stage} actions from roadmap...")
            
            input_data = {
                "active_path": active_path,
                "student_profile": context["student_profile"],
                "progress": progress,
                "completed_actions": context["current_actions"].get("completed_actions", []),
                "current_step": current_step + 1,
                "stage_number": next_stage
            }
            
            # Generate next stage actions
            result = self.action_agent.generate_actions(user_id=user_id)
            
            if result["status"] == "success":
                action_plan = result["action_plan"]
                next_stage_actions = action_plan.get("priority_actions", [])
                
                # Tag new actions with stage number
                for action in next_stage_actions:
                    action["stage"] = next_stage
                    action["status"] = "pending"
                
                # Update context with new stage actions
                context["current_actions"]["pending_actions"] = next_stage_actions
                context["current_actions"]["completed_actions"] = context["current_actions"].get("completed_actions", [])
                
                # Update progress
                progress["current_step"] = current_step + 1
                progress["last_stage_generated"] = datetime.now().isoformat()
                progress["stage_progression_history"] = progress.get("stage_progression_history", [])
                progress["stage_progression_history"].append({
                    "stage": next_stage,
                    "generated_at": datetime.now().isoformat(),
                    "action_count": len(next_stage_actions)
                })
                
                context["progress"] = progress
                
                # Allocate first action of new stage
                if next_stage_actions:
                    next_stage_actions[0]["status"] = "in_progress"
                    progress["next_action_allocated"] = next_stage_actions[0].get("title")
                    progress["last_allocation_time"] = datetime.now().isoformat()
                
                self.context_manager.save_context(user_id, context)
                print(f"✅ Stage {next_stage} generated with {len(next_stage_actions)} actions")
            
        except Exception as e:
            print(f"Error generating next stage: {e}")
    
    def _allocate_next_action(self, user_id: str, context: Dict[str, Any]) -> None:
        """Mark next pending action as current/prioritized"""
        pending = context.get("current_actions", {}).get("pending_actions", [])
        if pending:
            pending[0]["status"] = "in_progress"
            context["progress"]["next_action_allocated"] = pending[0].get("title")
            context["progress"]["last_allocation_time"] = datetime.now().isoformat()
    
    def record_blocker(self, user_id: str, action_id: str, description: str, attempted_solutions: List[str] = None) -> Dict[str, Any]:
        """Record a blocker"""
        result = self.feedback_agent.record_blocker(
            user_id=user_id,
            action_id=action_id,
            blocker_description=description,
            attempted_solutions=attempted_solutions
        )
        if result["status"] == "success":
            print(f"Blocker recorded for action '{action_id}'")
        return result
    
    def get_student_context(self, user_id: str) -> Dict[str, Any]:
        """Get complete student context"""
        return self.context_manager.get_full_context(user_id)
    
    def export_context(self, user_id: str, export_path: str = None) -> str:
        """Export user context to file"""
        return self.context_manager.export_context(user_id, export_path)
    
    def apply_alternative_path(self, user_id: str, alternative_path: Dict[str, Any], path_type: str = "alternative", option_index: int = None) -> Dict[str, Any]:
        """Apply a selected alternative path and update all context"""
        print(f"\nApplying alternative path for {user_id}...")
        
        try:
            context = self.context_manager.load_context(user_id)
            
            if not context["active_path"].get("original_target_role"):
                context["active_path"]["original_target_role"] = context["active_path"].get("target_role")
            
            path_change = {
                "timestamp": datetime.now().isoformat(),
                "type": path_type,
                "from_role": context["active_path"].get("target_role"),
                "to_role": alternative_path.get("new_target_role"),
                "option_index": option_index,
                "success_probability": alternative_path.get("success_probability", 0.0),
                "reason": "User selected after rerouting analysis"
            }
            
            if path_type == "alternative":
                context["active_path"]["target_role"] = alternative_path.get("new_target_role")
                context["active_path"]["success_probability"] = alternative_path.get("success_probability", 0.0)
                context["active_path"]["status"] = "not_started"
                context["active_path"]["current_path_type"] = "alternative"
            else:
                context["active_path"]["status"] = "not_started"
                context["active_path"]["current_path_type"] = "adjusted_original"
                if "extended_timeline_months" in alternative_path:
                    context["active_path"]["original_timeline_months"] = alternative_path.get("extended_timeline_months")
            
            context["active_path"]["path_change_history"].append(path_change)
            
            context["reroute_history"]["reroute_count"] += 1
            context["reroute_history"]["selected_alternative"] = {
                "selected_role": alternative_path.get("new_target_role"),
                "timestamp": datetime.now().isoformat(),
                "type": path_type
            }
            context["reroute_history"]["applied_changes"].append({
                "timestamp": datetime.now().isoformat(),
                "change": f"Applied {path_type}: {alternative_path.get('new_target_role')}"
            })
            
            context["progress"]["completed_steps"] = []
            context["progress"]["current_step"] = None
            context["progress"]["completion_rate"] = 0.0
            context["progress"]["time_spent_hours"] = 0.0
            
            context["current_actions"]["completed_actions"].extend(context["current_actions"]["pending_actions"])
            context["current_actions"]["pending_actions"] = []
            context["current_actions"]["priority_actions"] = []
            
            self.context_manager.save_context(user_id, context)
            
            print(f"  Regenerating career path for new role: {alternative_path.get('new_target_role')}")
            path_result = self.path_agent.generate_path(user_id=user_id, duration_weeks=12)
            
            print(f"  Generating new action plan")
            action_result = self.action_agent.generate_actions(user_id=user_id)
            
            print(f"  Regenerating feedback for new context")
            feedback_result = self.feedback_agent.evaluate_progress(user_id=user_id)
            
            consistency_check = self._validate_consistency(user_id)
            
            return {
                "status": "success",
                "message": f"Successfully applied alternative path: {alternative_path.get('new_target_role')}",
                "path_change": path_change,
                "consistency_check": consistency_check,
                "agents_updated": ["path_planning", "action_recommendation", "feedback_learning"],
                "new_context": self.context_manager.load_context(user_id)
            }
            
        except Exception as e:
            print(f"Error applying alternative path: {str(e)}")
            return {
                "status": "failure",
                "message": f"Failed to apply alternative path: {str(e)}",
                "error": str(e)
            }
    
    def apply_adjusted_original_path(self, user_id: str, adjusted_path: Dict[str, Any]) -> Dict[str, Any]:
        """Apply adjusted version of original path (extended timeline, modifications)"""
        print(f"\nApplying adjusted original path for {user_id}...")
        
        try:
            context = self.context_manager.load_context(user_id)
            
            # Update timeline and modifications
            if "extended_timeline_months" in adjusted_path:
                context["active_path"]["timeline_months"] = adjusted_path["extended_timeline_months"]
            
            # Mark as adjusted
            context["active_path"]["is_adjusted"] = True
            context["active_path"]["adjustment_reason"] = "User selected adjusted timeline due to high deviation risk"
            
            path_change = {
                "timestamp": datetime.now().isoformat(),
                "type": "adjusted_original",
                "role": context["active_path"].get("target_role"),
                "new_timeline_months": adjusted_path.get("extended_timeline_months"),
                "modifications": adjusted_path.get("modifications", []),
                "reason": "User adjusted pace to reduce deviation risk"
            }
            
            context["active_path"]["path_change_history"].append(path_change)
            
            context["reroute_history"]["reroute_count"] += 1
            context["reroute_history"]["selected_alternative"] = {
                "selected_option": "adjusted_original",
                "timestamp": datetime.now().isoformat(),
                "new_timeline": adjusted_path.get("extended_timeline_months")
            }
            
            self.context_manager.save_context(user_id, context)
            
            print(f"  Applied adjusted timeline: {adjusted_path.get('extended_timeline_months')} months")
            
            return {
                "status": "success",
                "message": f"Successfully applied adjusted original path with extended timeline",
                "path_change": path_change,
                "new_context": self.context_manager.load_context(user_id)
            }
            
        except Exception as e:
            print(f"Error applying adjusted original path: {str(e)}")
            return {
                "status": "failure",
                "message": f"Failed to apply adjusted original path: {str(e)}",
                "error": str(e)
            }
    
    def _validate_consistency(self, user_id: str) -> Dict[str, Any]:
        """Validate that all agents' data is consistent and relevant"""
        print(f"  Validating consistency across all agents...")
        
        context = self.context_manager.load_context(user_id)
        issues = []
        fixes = []
        
        current_goal = context["career_goals"].get("current_goal")
        active_role = context["active_path"].get("target_role")
        
        # Handle current_goal being either a string or dict
        if isinstance(current_goal, dict):
            current_goal = current_goal.get("target_role") or current_goal.get("role_title")
        
        if current_goal and active_role and str(current_goal).lower() != str(active_role).lower():
            issue = f"Goal mismatch: Career goal '{current_goal}' != Active path '{active_role}'"
            issues.append(issue)
            context["career_goals"]["current_goal"] = active_role
            context["career_goals"]["interpreted_goal"]["role_title"] = active_role
            fixes.append(f"Fixed: Updated career goal to '{active_role}'")
        
        if context["active_path"].get("primary_path"):
            path_skills = self._extract_skills_from_path(context["active_path"]["primary_path"])
            required_skills = context["career_goals"].get("interpreted_goal", {}).get("required_skills", [])
            
            missing_skills = set(required_skills) - set(path_skills)
            if missing_skills:
                issue = f"Skills gap: Required skills {list(missing_skills)} not in path"
                issues.append(issue)
                fixes.append(f"Note: Path missing skills {list(missing_skills)} - agents should address")
        
        pending_actions = context["current_actions"].get("pending_actions", [])
        action_count = len(pending_actions)
        
        if action_count == 0 and context["active_path"]["status"] != "completed":
            issue = f"No pending actions for active path '{active_role}'"
            issues.append(issue)
            fixes.append("Regenerating action plan...")
            self.action_agent.generate_actions(user_id=user_id)
        
        confidence = context["readiness"].get("confidence_score", 0.5)
        if confidence < 0.4:
            issue = f"Low confidence ({confidence:.2f}) - may need reassessment"
            issues.append(issue)
            fixes.append("Readiness reassessment recommended after path change")
        
        completion_rate = context["progress"].get("completion_rate", 0.0)
        path_status = context["active_path"].get("status")
        
        if path_status == "not_started" and completion_rate > 0:
            issue = f"Status mismatch: Path status '{path_status}' but completion {completion_rate*100:.0f}%"
            issues.append(issue)
            context["progress"]["completed_steps"] = []
            context["progress"]["completion_rate"] = 0.0
            fixes.append("Reset progress tracking for new path")
        
        self.context_manager.save_context(user_id, context)
        
        return {
            "consistent": len(issues) == 0,
            "issues_found": issues,
            "fixes_applied": fixes,
            "total_issues": len(issues),
            "total_fixes": len(fixes)
        }
    
    def _extract_skills_from_path(self, path: Dict[str, Any]) -> List[str]:
        """Extract all skills mentioned in a career path"""
        skills = set()
        
        if isinstance(path, dict):
            steps = path.get("steps", [])
            for step in steps:
                if isinstance(step, dict):
                    step_skills = step.get("skills", [])
                    if isinstance(step_skills, list):
                        skills.update(step_skills)
        
        return list(skills)
    
    def revert_to_original_path(self, user_id: str) -> Dict[str, Any]:
        """Revert from alternative path back to original target path after completing mission"""
        print(f"\nReverting to original path for {user_id}...")
        
        try:
            context = self.context_manager.load_context(user_id)
            
            # Check if there's an original path to revert to
            original_role = context["active_path"].get("original_target_role")
            if not original_role:
                return {
                    "status": "error",
                    "message": "No original path found to revert to"
                }
            
            # Check if alternative path is sufficiently completed
            alternative_role = context["active_path"].get("target_role")
            completion_on_alternative = context["progress"].get("completion_rate", 0)
            
            if completion_on_alternative < 0.6:  # At least 60% completion
                return {
                    "status": "warning",
                    "message": f"Alternative path only {completion_on_alternative*100:.0f}% complete. Recommend more progress before reverting."
                }
            
            # Record the reversal
            path_change = {
                "timestamp": datetime.now().isoformat(),
                "type": "reversion",
                "from_role": alternative_role,
                "to_role": original_role,
                "reason": "Reverted after completing alternative mission",
                "alternative_completion": completion_on_alternative
            }
            
            # Update context
            context["active_path"]["target_role"] = original_role
            context["active_path"]["status"] = "resumed"
            context["active_path"]["current_path_type"] = "original"
            context["active_path"]["path_change_history"].append(path_change)
            
            context["reroute_history"]["reroute_count"] += 1
            context["reroute_history"]["applied_changes"].append({
                "timestamp": datetime.now().isoformat(),
                "change": f"Reverted from {alternative_role} back to original path: {original_role}"
            })
            
            # Keep progress but mark as resumed
            context["progress"]["status"] = "resumed_from_alternative"
            context["progress"]["alternative_completion_rate"] = completion_on_alternative
            context["progress"]["last_reversion_time"] = datetime.now().isoformat()
            
            self.context_manager.save_context(user_id, context)
            
            print(f"  Regenerating career path for reverted role: {original_role}")
            path_result = self.path_agent.generate_path(user_id=user_id, duration_weeks=12)
            
            print(f"  Generating new action plan")
            action_result = self.action_agent.generate_actions(user_id=user_id)
            
            print(f"  Regenerating feedback")
            feedback_result = self.feedback_agent.evaluate_progress(user_id=user_id)
            
            consistency_check = self._validate_consistency(user_id)
            
            return {
                "status": "success",
                "message": f"Successfully reverted to original path: {original_role}",
                "path_change": path_change,
                "consistency_check": consistency_check,
                "new_context": self.context_manager.load_context(user_id)
            }
            
        except Exception as e:
            print(f"Error reverting to original path: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to revert path: {str(e)}",
                "error": str(e)
            }
    
    def get_next_action(self, user_id: str) -> Dict[str, Any]:
        """Get the next pending action allocated for the student"""
        context = self.context_manager.load_context(user_id)
        pending = context.get("current_actions", {}).get("pending_actions", [])
        
        if not pending:
            return {
                "status": "no_actions",
                "message": "All actions completed!",
                "action": None
            }
        
        next_action = pending[0]
        return {
            "status": "success",
            "action": next_action,
            "total_pending": len(pending)
        }
    
    # ==================== NEW FLOW: ROADMAP & STEP-BASED PROGRESSION ====================
    
    def generate_roadmap(self, user_id: str) -> Dict[str, Any]:
        """
        Generate a comprehensive roadmap with multiple steps.
        Each step contains 3 initial actions.
        Returns structured roadmap stored in user context.
        """
        print(f"\n{'='*70}")
        print(f"GENERATING ROADMAP for {user_id}...")
        print(f"{'='*70}")
        self._log_api_usage("ROADMAP_GENERATION", "CareerPathPlanningAgent", 2)
        
        try:
            context = self.context_manager.load_context(user_id)
            target_role = context["active_path"]["target_role"]
            
            prompt = f"""Generate a structured career development roadmap for reaching the role: {target_role}

Student Profile:
- Experience Level: {context['student_profile'].get('experience_level', 'unknown')}
- Learning Capacity: {context['student_profile'].get('learning_capacity', 'medium')}
- Weak Areas: {', '.join(context['readiness'].get('weak_areas', []))}
- Strengths: {context['student_profile'].get('strength_areas', [])}

Create a roadmap with 4-6 sequential steps. Each step should:
1. Have a clear title and description
2. Include exactly 3 actions initially
3. Each action needs success criteria for validation

Return ONLY valid JSON:
{{
  "roadmap": {{
    "total_steps": 5,
    "target_role": "{target_role}",
    "steps": [
      {{
        "step_number": 1,
        "title": "Foundation Building",
        "description": "Establish core fundamentals",
        "actions": [
          {{
            "action_id": "action_1_1",
            "title": "Learn Python Basics",
            "description": "Master Python fundamentals",
            "success_criteria": "Complete 10 coding exercises with 80%+ accuracy"
          }},
          {{
            "action_id": "action_1_2",
            "title": "Understand Data Structures",
            "description": "Learn arrays, lists, dictionaries",
            "success_criteria": "Implement all basic data structures from scratch"
          }},
          {{
            "action_id": "action_1_3",
            "title": "Problem Solving Practice",
            "description": "Solve algorithmic challenges",
            "success_criteria": "Solve 20+ problems on LeetCode/HackerRank"
          }}
        ]
      }}
    ]
  }}
}}"""
            
            content = self._call_llm_with_retry(prompt, max_tokens=3000)
            
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if not json_match:
                raise ValueError("Failed to extract JSON from LLM response")
            
            roadmap_data = json.loads(json_match.group())
            
            # Structure roadmap in context
            roadmap_structure = {
                "roadmap_id": f"{user_id}_roadmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "total_steps": roadmap_data["roadmap"]["total_steps"],
                "steps": [],
                "current_step_number": 1,
                "completed_steps": [],
                "created_at": datetime.now().isoformat(),
                "status": "in_progress"
            }
            
            # Initialize all steps with structure
            for step_data in roadmap_data["roadmap"]["steps"]:
                step = {
                    "step_number": step_data["step_number"],
                    "title": step_data["title"],
                    "description": step_data["description"],
                    "actions": [],
                    "status": "pending" if step_data["step_number"] > 1 else "in_progress",
                    "completion_percentage": 0.0
                }
                
                # Add actions to step
                for action_data in step_data.get("actions", []):
                    action = {
                        "action_id": action_data["action_id"],
                        "title": action_data["title"],
                        "description": action_data["description"],
                        "success_criteria": action_data.get("success_criteria", ""),
                        "status": "pending",
                        "questions": [],
                        "user_answers": [],
                        "relevance_score": 0.0,
                        "agent_satisfied": False,
                        "attempts": 0,
                        "completion_timestamp": None
                    }
                    step["actions"].append(action)
                
                roadmap_structure["steps"].append(step)
            
            context["roadmap"] = roadmap_structure
            self.context_manager.save_context(user_id, context)
            
            print(f"✅ Roadmap generated: {roadmap_structure['total_steps']} steps")
            print(f"   First step: {roadmap_structure['steps'][0]['title']}")
            print(f"   First step actions: {len(roadmap_structure['steps'][0]['actions'])} actions")
            
            return {
                "status": "success",
                "roadmap": roadmap_structure,
                "message": f"Roadmap generated with {roadmap_structure['total_steps']} steps"
            }
            
        except Exception as e:
            print(f"Error generating roadmap: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def complete_action_in_roadmap(self, user_id: str, step_number: int, action_id: str) -> Dict[str, Any]:
        """
        Mark an action as complete in the roadmap.
        Delegate to ActionRecommendationAgent to generate validation questions.
        Search in both roadmap steps and current_actions.
        """
        print(f"\nCompleting action {action_id} in step {step_number}...")
        
        try:
            context = self.context_manager.load_context(user_id)
            roadmap = context.get("roadmap", {})
            
            # Find the action in roadmap steps first
            target_step = None
            target_action = None
            
            for step in roadmap.get("steps", []):
                if step["step_number"] == step_number:
                    target_step = step
                    for action in step.get("actions", []):
                        if action.get("action_id") == action_id or action.get("id") == action_id:
                            target_action = action
                            break
                    break
            
            # If not found in roadmap, search in current_actions
            if not target_action:
                all_actions = context.get("current_actions", {}).get("pending_actions", []) + context.get("current_actions", {}).get("completed_actions", [])
                for action in all_actions:
                    if action.get("action_id") == action_id or action.get("id") == action_id or action.get("title") == action_id:
                        target_action = action
                        break
            
            if not target_action:
                return {"status": "error", "message": "Action not found in roadmap or current actions"}
            
            # Mark action as in progress
            target_action["status"] = "in_progress"
            target_action["attempts"] = target_action.get("attempts", 0) + 1
            
            # DELEGATE TO ActionRecommendationAgent to generate questions
            print(f"→ Delegating to ActionRecommendationAgent for question generation...")
            result = self.action_agent.generate_validation_questions(user_id, target_action)
            
            if result["status"] == "success":
                questions = result.get("questions", [])
                target_action["questions"] = questions
                self.context_manager.save_context(user_id, context)
                
                return {
                    "status": "success",
                    "action_id": action_id,
                    "questions": questions,
                    "message": f"Generated {len(questions)} questions for action validation"
                }
            else:
                return {"status": "error", "message": result.get("message", "Failed to generate questions")}
            
        except Exception as e:
            print(f"Error completing action: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    def submit_action_answers(self, user_id: str, step_number: int, action_id: str, answers: List[str]) -> Dict[str, Any]:
        """
        Submit answers to validation questions.
        Delegate to FeedbackLearningAgent for evaluation.
        Search in both roadmap steps and current_actions.
        """
        print(f"\nEvaluating answers for action {action_id}...")
        
        try:
            context = self.context_manager.load_context(user_id)
            roadmap = context.get("roadmap", {})
            
            # Find the action in roadmap steps first
            target_step = None
            target_action = None
            
            for step in roadmap.get("steps", []):
                if step["step_number"] == step_number:
                    target_step = step
                    for action in step.get("actions", []):
                        if action.get("action_id") == action_id or action.get("id") == action_id:
                            target_action = action
                            break
                    break
            
            # If not found in roadmap, search in current_actions
            if not target_action:
                all_actions = context.get("current_actions", {}).get("pending_actions", []) + context.get("current_actions", {}).get("completed_actions", [])
                for action in all_actions:
                    if action.get("action_id") == action_id or action.get("id") == action_id or action.get("title") == action_id:
                        target_action = action
                        break
            
            if not target_action:
                return {"status": "error", "message": "Action not found in roadmap or current actions"}
            
            # Ensure required fields exist
            if "attempts" not in target_action:
                target_action["attempts"] = 0
            
            # Store user answers
            target_action["user_answers"] = answers
            
            # DELEGATE TO FeedbackLearningAgent to evaluate answers
            print(f"→ Delegating to FeedbackLearningAgent for answer evaluation...")
            evaluation = self.feedback_agent.evaluate_action_answers(user_id, target_action, answers)
            
            target_action["relevance_score"] = evaluation.get("relevance_score", 0)
            target_action["agent_satisfied"] = evaluation.get("agent_satisfied", False)
            
            if evaluation.get("agent_satisfied"):
                target_action["status"] = "completed"
                target_action["completion_timestamp"] = datetime.now().isoformat()
                print(f"✅ Action '{action_id}' marked COMPLETE (score: {evaluation['relevance_score']:.2f})")
                
                # Check if step is complete
                self._check_step_completion(user_id, context, step_number)
            else:
                target_action["status"] = "pending"
                print(f"⏸️  Action '{action_id}' needs more work (score: {evaluation['relevance_score']:.2f})")
                
                # Auto-detect deviation after 3 failed attempts
                if target_action.get("attempts", 0) >= 3:
                    print(f"⚠️  AUTO-DETECTED: Action failed {target_action['attempts']} times. Triggering rerouting...")
                    context["reroute_state"]["is_rerouting"] = True
                    context["reroute_state"]["auto_detected"] = True
                    context["reroute_state"]["failed_action_id"] = action_id
                    context["reroute_state"]["failure_reason"] = f"Repeated failure on action: {target_action.get('title', 'Unknown')}"
            
            self.context_manager.save_context(user_id, context)
            
            return {
                "status": "success",
                "action_id": action_id,
                "relevance_score": evaluation.get("relevance_score", 0),
                "agent_satisfied": evaluation.get("agent_satisfied", False),
                "feedback": evaluation.get("feedback", ""),
                "next_steps": evaluation.get("next_steps", "")
            }
            
        except Exception as e:
            print(f"Error evaluating answers: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "message": str(e)}
    
    
    def _check_step_completion(self, user_id: str, context: Dict[str, Any], step_number: int) -> None:
        """Check if all actions in a step are complete. If yes, move to next step."""
        roadmap = context.get("roadmap", {})
        
        # Find the step
        target_step = None
        for step in roadmap.get("steps", []):
            if step["step_number"] == step_number:
                target_step = step
                break
        
        if not target_step:
            return
        
        # Check completion
        completed_actions = sum(1 for a in target_step.get("actions", []) if a.get("agent_satisfied"))
        total_actions = len(target_step.get("actions", []))
        
        target_step["completion_percentage"] = (completed_actions / total_actions) if total_actions > 0 else 0.0
        
        # If all actions satisfied, move to next step
        if completed_actions == total_actions and total_actions > 0:
            print(f"\n🎉 Step {step_number} COMPLETE!")
            target_step["status"] = "completed"
            roadmap["completed_steps"].append(step_number)
            
            # Move to next step if available
            if step_number < roadmap.get("total_steps", 0):
                next_step_number = step_number + 1
                for step in roadmap.get("steps", []):
                    if step["step_number"] == next_step_number:
                        step["status"] = "in_progress"
                        roadmap["current_step_number"] = next_step_number
                        print(f"✅ Starting Step {next_step_number}: {step['title']}")
                        break
            else:
                # All steps complete!
                roadmap["status"] = "completed"
                print(f"\n🏆 ALL STEPS COMPLETE! Roadmap finished!")
            
            self.context_manager.save_context(user_id, context)
    
    def get_roadmap_status(self, user_id: str) -> Dict[str, Any]:
        """Get current roadmap status and progress"""
        context = self.context_manager.load_context(user_id)
        roadmap = context.get("roadmap", {})
        
        if not roadmap or not roadmap.get("steps"):
            return {
                "status": "no_roadmap",
                "message": "No roadmap generated yet"
            }
        
        current_step_num = roadmap.get("current_step_number", 1)
        current_step = None
        pending_actions = []
        
        for step in roadmap.get("steps", []):
            if step["step_number"] == current_step_num:
                current_step = step
                pending_actions = [a for a in step.get("actions", []) if a.get("status") != "completed"]
                break
        
        total_completed_steps = len(roadmap.get("completed_steps", []))
        total_steps = roadmap.get("total_steps", 0)
        
        return {
            "status": "success",
            "roadmap_id": roadmap.get("roadmap_id"),
            "current_step": current_step_num,
            "current_step_title": current_step.get("title") if current_step else None,
            "completed_steps": total_completed_steps,
            "total_steps": total_steps,
            "progress_percentage": (total_completed_steps / total_steps * 100) if total_steps > 0 else 0,
            "pending_actions_in_current_step": pending_actions,
            "roadmap_status": roadmap.get("status", "unknown")
        }
    
    # ==================== REROUTING WITH ROADMAP ====================
    
    def detect_deviation_and_reroute(self, user_id: str, deviation_reason: str) -> Dict[str, Any]:
        """
        Detect deviation and create alternative roadmaps.
        User can select one or continue with adjusted original.
        """
        print(f"\n{'='*70}")
        print(f"DETECTING DEVIATION & GENERATING ALTERNATIVES for {user_id}...")
        print(f"{'='*70}")
        self._log_api_usage("REROUTING", "ReroutingAgent", 3)
        
        try:
            context = self.context_manager.load_context(user_id)
            original_role = context["active_path"]["target_role"]
            
            prompt = f"""The student has deviated from their career path to {original_role}.

Deviation Reason: {deviation_reason}

Based on this deviation and their profile, suggest:
1. Two alternative career paths that leverage their new direction
2. An adjusted version of the original path that accommodates the deviation

For each option, provide a brief roadmap outline.

Return ONLY valid JSON:
{{
  "alternatives": [
    {{
      "option_id": 1,
      "new_target_role": "Alternative Role 1",
      "reason": "Why this alternative",
      "success_probability": 0.75,
      "timeline_months": 12,
      "brief_roadmap": "Step 1: ..., Step 2: ..."
    }}
  ],
  "adjusted_original": {{
    "option_id": "original_adjusted",
    "original_target_role": "{original_role}",
    "adjustment": "How to adjust the original path",
    "timeline_months": 15,
    "brief_roadmap": "Adjusted Step 1: ..., Adjusted Step 2: ..."
  }}
}}"""
            
            content = self._call_llm_with_retry(prompt, max_tokens=2000)
            
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if not json_match:
                raise ValueError("Failed to extract JSON")
            
            reroute_data = json.loads(json_match.group())
            
            # Store alternatives in context
            context["reroute_state"]["is_rerouting"] = True
            context["reroute_state"]["original_roadmap_id"] = context["roadmap"].get("roadmap_id")
            context["reroute_state"]["alternative_roadmaps"] = reroute_data.get("alternatives", [])
            context["reroute_state"]["reroute_timestamp"] = datetime.now().isoformat()
            context["reroute_state"]["reroute_reason"] = deviation_reason
            
            self.context_manager.save_context(user_id, context)
            
            return {
                "status": "success",
                "rerouting_active": True,
                "original_role": original_role,
                "alternatives": reroute_data.get("alternatives", []),
                "adjusted_original": reroute_data.get("adjusted_original", {}),
                "message": f"Generated alternatives for deviation: {deviation_reason}"
            }
            
        except Exception as e:
            print(f"Error during rerouting: {e}")
            return {"status": "error", "message": str(e)}
    
    def select_reroute_option(self, user_id: str, option_id) -> Dict[str, Any]:
        """
        User selects a reroute option.
        Generate new roadmap and update context.
        """
        print(f"\nApplying selected reroute option for {user_id}...")
        
        try:
            context = self.context_manager.load_context(user_id)
            reroute_state = context.get("reroute_state", {})
            
            if not reroute_state.get("is_rerouting"):
                return {"status": "error", "message": "No active rerouting"}
            
            selected_alternative = None
            is_adjusted_original = False
            
            # Find selected option
            if option_id == "original_adjusted":
                # User selected adjusted original
                is_adjusted_original = True
                selected_alternative = reroute_state.get("adjusted_original", {})
                new_role = context["active_path"]["target_role"]
            else:
                # User selected an alternative
                for alt in reroute_state.get("alternative_roadmaps", []):
                    if alt.get("option_id") == option_id:
                        selected_alternative = alt
                        new_role = alt.get("new_target_role")
                        break
            
            if not selected_alternative:
                return {"status": "error", "message": "Selected option not found"}
            
            # Update context with selected reroute
            context["reroute_state"]["selected_alternative_id"] = option_id
            context["reroute_state"]["is_rerouting"] = False
            
            if not is_adjusted_original:
                context["active_path"]["target_role"] = new_role
                context["active_path"]["current_path_type"] = "rerouted"
                context["reroute_history"]["reroute_count"] += 1
                context["reroute_history"]["selected_alternative"] = {
                    "new_role": new_role,
                    "timestamp": datetime.now().isoformat(),
                    "reason": reroute_state.get("reroute_reason")
                }
            
            # Generate new roadmap
            print(f"  Generating new roadmap for role: {new_role}")
            roadmap_result = self.generate_roadmap(user_id)
            
            if roadmap_result["status"] != "success":
                return {"status": "error", "message": "Failed to generate new roadmap"}
            
            self.context_manager.save_context(user_id, context)
            
            return {
                "status": "success",
                "message": f"Applied reroute option, new roadmap generated",
                "new_target_role": new_role,
                "is_adjusted_original": is_adjusted_original,
                "roadmap": roadmap_result.get("roadmap")
            }
            
        except Exception as e:
            print(f"Error applying reroute: {e}")
            return {"status": "error", "message": str(e)}
    
    def complete_rerouted_roadmap(self, user_id: str) -> Dict[str, Any]:
        """
        Student completes rerouted roadmap.
        Redirect back to original target if applicable.
        """
        print(f"\nCompleting rerouted roadmap for {user_id}...")
        
        try:
            context = self.context_manager.load_context(user_id)
            reroute_state = context.get("reroute_state", {})
            original_roadmap_id = reroute_state.get("original_roadmap_id")
            
            if not original_roadmap_id:
                return {
                    "status": "success",
                    "message": "Rerouted roadmap completed! No original roadmap to return to.",
                    "next_step": "You have successfully completed your career development!"
                }
            
            # Regenerate original roadmap
            print(f"  Regenerating original roadmap...")
            
            # Store reroute completion info
            reroute_state["alternative_completion_percentage"] = 1.0
            reroute_state["redirect_to_step"] = 1  # Start fresh on original
            context["reroute_state"] = reroute_state
            
            self.context_manager.save_context(user_id, context)
            
            # Now user can be re-directed to original path
            return {
                "status": "success",
                "message": "Rerouted roadmap completed!",
                "redirect_available": True,
                "redirect_message": "You can now return to your original career target!",
                "next_action": "User can choose to return to original path or continue with current"
            }
            
        except Exception as e:
            print(f"Error completing rerouted roadmap: {e}")
            return {"status": "error", "message": str(e)}
