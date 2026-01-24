"""
User Context Manager
Manages persistent storage and retrieval of all user-related data
across agent interactions.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class UserContextManager:
    """
    Centralized manager for user context that persists across sessions.
    All agents MUST read from and write to this context.
    """
    
    def __init__(self, context_dir: str = None):
        """
        Initialize context manager
        
        Args:
            context_dir: Directory to store user context files
        """
        if context_dir is None:
            # Default to data/user_contexts folder
            context_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_contexts")
        
        self.context_dir = Path(context_dir)
        self.context_dir.mkdir(exist_ok=True, parents=True)
    
    def get_context_path(self, user_id: str) -> Path:
        """Get file path for user context"""
        return self.context_dir / f"{user_id}_context.json"
    
    def initialize_context(self, user_id: str) -> Dict[str, Any]:
        """
        Initialize a new user context
        
        Returns:
            Fresh user context structure
        """
        context = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            
            # Student Profile (managed by Student Profiling Agent)
            "student_profile": {
                "personal_info": {
                    "education": None,
                    "current_year": None,
                    "institution": None
                },
                "experience_level": None,
                "technical_skills": {},
                "soft_skills": [],
                "strength_areas": [],
                "weakness_areas": [],
                "learning_capacity": None,
                "risk_factors": [],
                "projects": [],
                "experience": None
            },
            
            # Career Goals (managed by Goal Interpretation Agent)
            "career_goals": {
                "current_goal": None,
                "interpreted_goal": None,
                "goal_history": [],
                "goal_clarity_score": 0.0,
                "commitment_level": None
            },
            
            # Readiness Assessment (managed by Readiness Assessment Agent)
            "readiness": {
                "confidence_score": 0.0,
                "deviation_risk": None,
                "weak_areas": [],
                "diagnostic_questions": [],
                "diagnostic_answers": [],
                "readiness_verdict": None,
                "last_assessed": None
            },
            
            # Market Context (managed by Market Intelligence Agent)
            "market_context": {
                "target_role_analysis": None,
                "last_market_check": None,
                "market_trends": []
            },
            
            # Active Career Path (managed by Career Path Planning Agent)
            "active_path": {
                "path_id": None,
                "target_role": None,
                "primary_path": None,
                "fallback_paths": [],
                "success_probability": 0.0,
                "created_at": None,
                "status": "not_started",
                "original_target_role": None,
                "path_change_history": [],
                "current_path_type": "original"
            },
            
            # Roadmap & Step Progression (managed by Orchestrator)
            "roadmap": {
                "roadmap_id": None,
                "total_steps": 0,
                "steps": [
                    # Each step: {
                    #   "step_number": 1,
                    #   "title": "Foundation Building",
                    #   "description": "...",
                    #   "actions": [
                    #     {
                    #       "action_id": "action_1",
                    #       "title": "Learn Python Basics",
                    #       "description": "...",
                    #       "status": "pending/in_progress/completed/failed",
                    #       "questions": [...],  # 5 questions generated
                    #       "user_answers": [...],  # User's answers to questions
                    #       "relevance_score": 0.85,  # Agent calculated score 0-1
                    #       "agent_satisfied": false,  # Is agent satisfied with completion?
                    #       "attempts": 0,  # Number of times user attempted
                    #       "completion_timestamp": None
                    #     }
                    #   ],
                    #   "status": "pending/in_progress/completed",
                    #   "completion_percentage": 0.0
                    # }
                ],
                "current_step_number": None,
                "completed_steps": [],
                "created_at": None,
                "status": "generated/in_progress/completed"
            },
            
            # Rerouting State (managed by Rerouting Agent)
            "reroute_state": {
                "is_rerouting": False,
                "original_roadmap_id": None,
                "alternative_roadmaps": [],
                "selected_alternative_id": None,
                "alternative_completion_percentage": 0.0,
                "redirect_to_step": None,
                "reroute_timestamp": None,
                "reroute_reason": None
            },
            
            # Progress Tracking (managed by Feedback & Learning Agent)
            "progress": {
                "completed_steps": [],
                "current_step": None,
                "blockers": [],
                "time_spent_hours": 0.0,
                "completion_rate": 0.0,
                "last_activity": None,
                "active_stage": 1,
                "stage_completion_rate": 0.0,
                "stage_progression_history": [],
                "next_stage_generated_at": None,
                "next_action_allocated": None,
                "last_allocation_time": None
            },
            
            # Re-routing History (managed by Re-Routing Agent)
            "reroute_history": {
                "failed_paths": [],
                "reroute_reasons": [],
                "alternative_suggestions": [],
                "reroute_count": 0,
                "selected_alternative": None,
                "applied_changes": []
            },
            
            # Actions & Recommendations (managed by Action Agent)
            "current_actions": {
                "pending_actions": [],
                "completed_actions": [],
                "priority_actions": []
            },
            
            # System Metadata
            "metadata": {
                "total_sessions": 0,
                "agent_interaction_count": {},
                "system_events": []
            }
        }
        
        self.save_context(user_id, context)
        return context
    
    def load_context(self, user_id: str) -> Dict[str, Any]:
        """
        Load user context from storage
        
        Returns:
            User context dict or creates new if doesn't exist
        """
        context_path = self.get_context_path(user_id)
        
        if context_path.exists():
            with open(context_path, 'r') as f:
                context = json.load(f)
            return context
        else:
            return self.initialize_context(user_id)
    
    def save_context(self, user_id: str, context: Dict[str, Any]) -> None:
        """
        Save user context to storage
        """
        context["last_updated"] = datetime.now().isoformat()
        context_path = self.get_context_path(user_id)
        
        with open(context_path, 'w') as f:
            json.dump(context, indent=2, fp=f)
    
    def update_student_profile(self, user_id: str, profile_data: Dict[str, Any]) -> None:
        """Update student profile section"""
        context = self.load_context(user_id)
        context["student_profile"].update(profile_data)
        self.save_context(user_id, context)
    
    def update_career_goals(self, user_id: str, goal_data: Dict[str, Any]) -> None:
        """Update career goals section"""
        context = self.load_context(user_id)
        
        if context["career_goals"]["current_goal"] != goal_data.get("current_goal"):
            if context["career_goals"]["current_goal"]:
                context["career_goals"]["goal_history"].append({
                    "goal": context["career_goals"]["current_goal"],
                    "timestamp": datetime.now().isoformat(),
                    "reason": "goal_changed"
                })
        
        context["career_goals"].update(goal_data)
        self.save_context(user_id, context)
    
    def update_readiness(self, user_id: str, readiness_data: Dict[str, Any]) -> None:
        """Update readiness assessment"""
        context = self.load_context(user_id)
        readiness_data["last_assessed"] = datetime.now().isoformat()
        context["readiness"].update(readiness_data)
        self.save_context(user_id, context)
    
    def update_market_context(self, user_id: str, market_data: Dict[str, Any]) -> None:
        """Update market intelligence data"""
        context = self.load_context(user_id)
        market_data["last_market_check"] = datetime.now().isoformat()
        context["market_context"].update(market_data)
        self.save_context(user_id, context)
    
    def update_active_path(self, user_id: str, path_data: Dict[str, Any]) -> None:
        """Update active career path"""
        context = self.load_context(user_id)
        
        if not path_data.get("created_at"):
            path_data["created_at"] = datetime.now().isoformat()
        
        context["active_path"].update(path_data)
        self.save_context(user_id, context)
    
    def update_roadmap(self, user_id: str, roadmap_data: Dict[str, Any]) -> None:
        """Update roadmap with steps and actions"""
        context = self.load_context(user_id)
        
        if not roadmap_data.get("created_at"):
            roadmap_data["created_at"] = datetime.now().isoformat()
        
        # Initialize roadmap_id if not present
        if not roadmap_data.get("roadmap_id"):
            roadmap_data["roadmap_id"] = f"roadmap_{user_id}_{int(datetime.now().timestamp())}"
        
        # Ensure status is set
        if not roadmap_data.get("status"):
            roadmap_data["status"] = "generated"
        
        context["roadmap"].update(roadmap_data)
        self.save_context(user_id, context)
    
    def record_progress(self, user_id: str, progress_data: Dict[str, Any]) -> None:
        """Record progress update"""
        context = self.load_context(user_id)
        progress_data["last_activity"] = datetime.now().isoformat()
        
        if "completed_step" in progress_data:
            context["progress"]["completed_steps"].append(progress_data["completed_step"])
            del progress_data["completed_step"]
        
        if "blocker" in progress_data:
            context["progress"]["blockers"].append(progress_data["blocker"])
            del progress_data["blocker"]
        
        context["progress"].update(progress_data)
        self.save_context(user_id, context)
    
    def record_reroute(self, user_id: str, reroute_data: Dict[str, Any]) -> None:
        """Record re-routing event"""
        context = self.load_context(user_id)
        
        context["reroute_history"]["reroute_count"] += 1
        
        if "failed_path" in reroute_data:
            context["reroute_history"]["failed_paths"].append(reroute_data["failed_path"])
        
        if "reason" in reroute_data:
            context["reroute_history"]["reroute_reasons"].append({
                "reason": reroute_data["reason"],
                "timestamp": datetime.now().isoformat()
            })
        
        if "alternatives" in reroute_data:
            context["reroute_history"]["alternative_suggestions"].extend(
                reroute_data["alternatives"]
            )
        
        self.save_context(user_id, context)
    
    def update_actions(self, user_id: str, action_data: Dict[str, Any]) -> None:
        """Update current actions"""
        context = self.load_context(user_id)
        
        if "completed_action" in action_data:
            context["current_actions"]["completed_actions"].append(
                action_data["completed_action"]
            )
            del action_data["completed_action"]
        
        context["current_actions"].update(action_data)
        self.save_context(user_id, context)
    
    def log_agent_interaction(self, user_id: str, agent_name: str, 
                             event_type: str, details: Dict = None) -> None:
        """Log agent interaction for tracking"""
        context = self.load_context(user_id)
        
        if agent_name not in context["metadata"]["agent_interaction_count"]:
            context["metadata"]["agent_interaction_count"][agent_name] = 0
        context["metadata"]["agent_interaction_count"][agent_name] += 1
        
        context["metadata"]["system_events"].append({
            "agent": agent_name,
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        })
        
        if len(context["metadata"]["system_events"]) > 100:
            context["metadata"]["system_events"] = \
                context["metadata"]["system_events"][-100:]
        
        self.save_context(user_id, context)
    
    def get_full_context(self, user_id: str) -> Dict[str, Any]:
        """Get complete user context"""
        return self.load_context(user_id)
    
    def export_context(self, user_id: str, export_path: str = None) -> str:
        """Export user context to JSON file"""
        context = self.load_context(user_id)
        
        if not export_path:
            export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "exports")
            os.makedirs(export_dir, exist_ok=True)
            export_path = os.path.join(export_dir, 
                f"{user_id}_context_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(export_path, 'w') as f:
            json.dump(context, indent=2, fp=f)
        
        return export_path
    
    def clear_context(self, user_id: str) -> None:
        """Clear user context (use with caution)"""
        context_path = self.get_context_path(user_id)
        if context_path.exists():
            context_path.unlink()
