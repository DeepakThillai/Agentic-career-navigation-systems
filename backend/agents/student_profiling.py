"""
Student Profiling Agent
Analyzes student background to create comprehensive profile
"""

import json
import os
from typing import Dict, Any, Optional
import requests
from ..user_context import UserContextManager
from ..utils.api_client import APIClient
from ..utils.api_key_manager import get_key_manager


class StudentProfilingAgent:
    """
    Analyzes student academic, skill, and experience data
    to create a detailed profile for career guidance
    """
    
    AGENT_NAME = "Student Profiling Agent"
    AGENT_OBJECTIVE = (
        "Analyze academic, aptitude, skill, engagement, and experience features. "
        "Infer strengths, gaps, learning velocity, and risk levels. "
        "Do NOT suggest careers or actions."
    )
    
    def __init__(self, context_manager: UserContextManager):
        """
        Initialize agent
        
        Args:
            context_manager: User context manager instance
        """
        self.context_manager = context_manager
        key_manager = get_key_manager()
        self.api_key = key_manager.get_key_for_agent("StudentProfilingAgent")
    
    def _call_llm(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Groq LLM with agent-specific prompt"""
        
        output_schema = """{
  "student_profile": {
    "experience_level": "beginner/intermediate/advanced",
    "technical_skills": {
      "programming": ["skill1", "skill2"],
      "web_development": ["skill1", "skill2"],
      "data_science": ["skill1", "skill2"],
      "tools": ["tool1", "tool2"]
    },
    "soft_skills": ["communication", "problem_solving"],
    "strength_areas": ["area1", "area2"],
    "weakness_areas": ["area1", "area2"],
    "learning_capacity": "slow/moderate/fast",
    "risk_factors": ["risk1", "risk2"],
    "profile_confidence": 0.0
  }
}"""
        
        system_prompt = f"""You are an autonomous agent operating inside an Agentic AI-Powered Career Navigation System.

AGENT_NAME: {self.AGENT_NAME}

AGENT_OBJECTIVE: {self.AGENT_OBJECTIVE}

INPUT_JSON:
{json.dumps(input_data, indent=2)}

RESPONSIBILITIES:
- Analyze academic, aptitude, skill, engagement, and experience features
- Infer strengths, gaps, learning velocity, and risk levels
- Be conservative in assessments
- Do NOT suggest careers or actions
- Focus on factual analysis only

OUTPUT_SCHEMA:
{output_schema}

Return ONLY valid JSON matching the schema. No markdown, no explanations."""

        try:
            result = APIClient.call_groq_api(
                api_key=self.api_key,
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = result["choices"][0]["message"]["content"]
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
            
        except Exception as e:
            print(f"LLM call error: {e}")
            raise
    
    def analyze_profile(self, 
                       user_id: str,
                       skills_text: str = None,
                       education: str = None,
                       experience: str = None,
                       projects: list = None,
                       resume_text: str = None) -> Dict[str, Any]:
        """
        Analyze student profile and update context
        
        Args:
            user_id: User identifier
            skills_text: Free-form skills description
            education: Education background
            experience: Work experience description
            projects: List of projects
            resume_text: Full resume text
            
        Returns:
            Analysis result with student profile
        """
        
        context = self.context_manager.load_context(user_id)
        
        input_data = {
            "new_input": {
                "skills_text": skills_text,
                "education": education,
                "experience": experience,
                "projects": projects or [],
                "resume_text": resume_text
            },
            "existing_profile": context["student_profile"]
        }
        
        result = self._call_llm(input_data)
        
        student_profile = result["student_profile"]
        
        self.context_manager.update_student_profile(user_id, student_profile)
        
        if education:
            self.context_manager.update_student_profile(user_id, {
                "personal_info": {
                    "education": education
                }
            })
        
        if experience:
            self.context_manager.update_student_profile(user_id, {
                "experience": experience
            })
        
        if projects:
            self.context_manager.update_student_profile(user_id, {
                "projects": projects
            })
        
        self.context_manager.log_agent_interaction(
            user_id,
            self.AGENT_NAME,
            "profile_analyzed",
            {
                "experience_level": student_profile.get("experience_level"),
                "skills_count": len(student_profile.get("technical_skills", {}))
            }
        )
        
        return {
            "agent": self.AGENT_NAME,
            "status": "success",
            "student_profile": student_profile,
            "context_updated": True
        }
