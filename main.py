"""
Main Execution Script
Interactive CLI for Career Navigation System
"""

import os
import sys
import json

# Add parent directory to path for backend imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize API Key Manager BEFORE any backend imports
from backend.utils.api_key_manager import initialize_key_manager
try:
    initialize_key_manager()
except ValueError as e:
    print(f"\n❌ Error: {e}")
    print("\n📝 Quick Fix - Use the launcher script:")
    print("   cd e:\\agents")
    print("   .\\start_with_3_keys.ps1")
    print("\n📝 Or set your API keys manually:")
    print("   $env:GROQ_API_KEY_1='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'")
    print("   $env:GROQ_API_KEY_2='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'")
    print("   $env:GROQ_API_KEY_3='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'")
    print("   python main.py")
    sys.exit(1)

# IMPORTANT: Apply request throttling BEFORE importing any backend modules
import requests
import time

_last_request_time = 0
_min_request_interval = 1.5
_original_post = requests.post

def _throttled_post(*args, **kwargs):
    """Wrapper around requests.post that adds global throttling"""
    global _last_request_time
    
    # Only throttle Groq API requests
    url = args[0] if args else kwargs.get('url', '')
    if 'groq.com' in str(url):
        elapsed = time.time() - _last_request_time
        if elapsed < _min_request_interval:
            time.sleep(_min_request_interval - elapsed)
        _last_request_time = time.time()
    
    return _original_post(*args, **kwargs)

requests.post = _throttled_post

from backend.orchestrator import Orchestrator


def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f" {text}")
    print(f"{'='*70}\n")


def print_section(text):
    """Print formatted section"""
    print(f"\n{'-'*70}")
    print(f" {text}")
    print(f"{'-'*70}\n")


def display_diagnostic_questions(questions):
    """Display diagnostic questions"""
    print_section("DIAGNOSTIC QUESTIONS")
    print("Please answer the following questions to assess your readiness:\n")
    
    for i, q in enumerate(questions, 1):
        print(f"Q{i}. {q['question']}")
        print(f"    Purpose: {q['purpose']}\n")


def display_career_path(path):
    """Display career path with reasoning"""
    print_section(f"CAREER PATH: {path['target_role']}")
    
    print(f"\nDuration: {path['estimated_duration_months']} months")
    print(f"Success Probability: {path['success_probability']*100:.0f}%\n")
    
    # Display path rationale if available
    if path.get("path_rationale"):
        print(f"Rationale: {path['path_rationale']}\n")
    
    print("PRIMARY PATH STEPS:")
    for step in path["primary_path"]["steps"]:
        print(f"\n{step['step_number']}. {step['title']} ({step['duration_weeks']} weeks)")
        print(f"   Description: {step.get('description', 'N/A')}")
        print(f"   Skills: {', '.join(step['skills_to_learn'])}")
        print(f"   Success Criteria: {step['success_criteria']}")
        if step.get('difficulty'):
            print(f"   Difficulty: {step['difficulty']}")
    
    if path.get("risk_factors"):
        print(f"\n\nRisk Factors:")
        for risk in path['risk_factors']:
            print(f"• {risk}")
    
    if path.get("confidence_boosters"):
        print(f"\n\nConfidence Boosters:")
        for boost in path['confidence_boosters']:
            print(f"• {boost}")
    
    if path["fallback_paths"]:
        print("\n\nFALLBACK OPTIONS:")
        for fb in path["fallback_paths"]:
            print(f"• {fb['alternative_role']}: {fb['reason']}")


def display_actions(action_plan):
    """Display action plan"""
    print_section("YOUR ACTION PLAN")
    
    print(f"Current Focus: {action_plan['current_focus']}\n")
    
    print("THIS WEEK:")
    this_week_ids = action_plan["this_week"]
    for action in action_plan["priority_actions"]:
        if action["action_id"] in this_week_ids:
            print(f"• {action['title']}")
            print(f"  Time: ~{action['estimated_hours']}h | Priority: {action['priority']}")
            print(f"  Impact: {action['impact_score']}/10 | Effort: {action['effort_score']}/10\n")
    
    print("\nQUICK WINS:")
    for win in action_plan["quick_wins"]:
        print(f"* {win}")


def interactive_onboarding():
    """Interactive onboarding flow"""
    print_header("CAREER NAVIGATION SYSTEM - ONBOARDING")
    
    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY environment variable not set")
        print("\nSet it with: export GROQ_API_KEY='your_key_here'")
        return None
    
    # Initialize orchestrator
    print("Initializing system...")
    orch = Orchestrator()
    
    # Collect user information
    print("\nLet's get started! Please provide your information:\n")
    
    user_id = input("User ID (e.g., student_001): ").strip() or f"student_{os.urandom(4).hex()}"
    print(f"Using user ID: {user_id}\n")
    
    desired_role = input("What career role are you targeting? (e.g., Data Scientist): ").strip()
    if not desired_role:
        print("Career role is required!")
        return None
    
    print("\nTell us about your background:")
    skills = input("Your skills (describe freely): ").strip()
    education = input("Education (e.g., 3rd year B.Tech CS): ").strip()
    experience = input("Work experience (optional): ").strip()
    
    projects_input = input("Projects (separate by semicolon ;): ").strip()
    projects = [p.strip() for p in projects_input.split(";") if p.strip()] if projects_input else None
    
    duration_input = input("How many weeks can you dedicate? (default 12): ").strip()
    try:
        duration_weeks = int(duration_input) if duration_input else 12
    except ValueError:
        duration_weeks = 12
    
    # Run onboarding
    print("\nProcessing your information through our agent system...")
    print("This may take a minute...\n")
    
    result = orch.onboard_student(
        user_id=user_id,
        desired_role=desired_role,
        skills=skills,
        education=education,
        experience=experience,
        projects=projects,
        duration_weeks=duration_weeks
    )
    
    if result["status"] != "success":
        print(f"\nError: {result.get('error', 'Unknown error')}")
        return None
    
    # Display results
    print_header("ONBOARDING COMPLETE!")
    
    summary = result["summary"]
    print(f"Target Role: {summary['target_role']}")
    print(f"Readiness: {summary['readiness']}")
    print(f"Market Demand: {summary['market_demand']}/100")
    print(f"Success Probability: {summary['success_probability']*100:.0f}%")
    print(f"Path Duration: {summary['path_duration_weeks']} weeks")
    print(f"Immediate Actions: {summary['immediate_actions']} tasks")
    
    # Show diagnostic questions
    readiness = result["agent_outputs"]["readiness"]["readiness_assessment"]
    display_diagnostic_questions(readiness["diagnostic_questions"])
    
    # Ask if user wants to answer
    answer = input("\nWould you like to answer these questions now? (y/n): ").strip().lower()
    
    if answer == 'y':
        print("\nPlease provide your answers:\n")
        answers = []
        for i, q in enumerate(readiness["diagnostic_questions"], 1):
            ans = input(f"Q{i}: ").strip()
            answers.append(ans)
        
        print("\nEvaluating your answers...")
        eval_result = orch.answer_diagnostic_questions(user_id, answers)
        
        if eval_result["status"] == "success":
            updated_assessment = eval_result["readiness_assessment"]
            print(f"\nUpdated Confidence Score: {updated_assessment['confidence_score']:.2f}")
            print(f"   Readiness: {updated_assessment['readiness_verdict']}")
    
    # Show career path
    career_path = result["agent_outputs"]["career_path"]["career_path"]
    display_career_path(career_path)
    
    # Show actions
    action_plan = result["agent_outputs"]["actions"]["action_plan"]
    display_actions(action_plan)
    
    # Export context
    export = input("\n\nExport your context to file? (y/n): ").strip().lower()
    if export == 'y':
        export_path = orch.export_context(user_id)
        print(f"Context exported to: {export_path}")
    
    print_header("READY TO START YOUR JOURNEY!")
    print(f"Your personalized plan has been created and saved.")
    print(f"User ID: {user_id}")
    print(f"\nNext steps:")
    print(f"1. Review your action plan above")
    print(f"2. Start with the tasks marked for 'THIS WEEK'")
    print(f"3. Track your progress and update the system")
    print(f"\nGood luck on your career journey!\n")
    
    return user_id, orch


def interactive_progress_tracking(user_id, orch):
    """Interactive progress tracking with auto-rerouting on low scores"""
    print_header("PROGRESS TRACKING")
    
    context = orch.get_student_context(user_id)
    
    # Check confidence score and auto-trigger rerouting if needed
    current_confidence = context["readiness"].get("confidence_score", 0.5)
    deviation_risk = context["readiness"].get("deviation_risk", "medium")
    
    if current_confidence < 0.4 or deviation_risk == "high":
        print(f"\nCONCERN DETECTED:")
        print(f"   Confidence Score: {current_confidence:.2f}/1.0")
        print(f"   Deviation Risk: {deviation_risk}")
        print(f"\nYour current path may need adjustment.\n")
        
        reroute_choice = input("Would you like to explore alternative paths? (y/n): ").strip().lower()
        if reroute_choice == 'y':
            reroute_result = orch.handle_failure_and_reroute(user_id)
            if reroute_result["status"] == "success":
                analysis = reroute_result["reroute_analysis"]
                print_section("REROUTING ANALYSIS")
                print(f"Failure Type: {analysis['failure_type']}\n")
                print(f"Reasons: {', '.join(analysis['failure_reasons'])}\n")
                print(f"Alternative Paths: {len(analysis['alternative_paths'])}")
                for i, alt in enumerate(analysis['alternative_paths'], 1):
                    print(f"  {i}. {alt['new_target_role']} ({alt['success_probability']*100:.0f}% success)")
                    print(f"     Why: {alt['why_better_fit']}")
            return
    
    actions = context["current_actions"]["pending_actions"]
    
    if not actions:
        print("No pending actions found.")
        print("\nOptions:")
        print("1. View completed actions")
        print("2. Generate new actions for next step")
        print("3. View full roadmap with reasoning")
        print("4. Return to menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            completed = context["current_actions"].get("completed_actions", [])
            if completed:
                print_section("COMPLETED ACTIONS")
                for action in completed:
                    print(f"✓ {action['title']}")
                    if action.get('time_spent_hours'):
                        print(f"   Time: {action['time_spent_hours']}h")
            else:
                print("No completed actions yet.")
        
        elif choice == "2":
            # Move to next step
            current_step = context["progress"].get("current_step")
            path = context.get("active_path", {})
            
            if path.get("primary_path"):
                steps = path["primary_path"]["steps"]
                next_step_num = (current_step or 0) + 1
                
                if next_step_num <= len(steps):
                    next_step = steps[next_step_num - 1]
                    print_section(f"NEXT STEP: {next_step['title']}")
                    print(f"\nDescription: {next_step.get('description', 'N/A')}")
                    print(f"Duration: {next_step['duration_weeks']} weeks")
                    print(f"Skills to Learn: {', '.join(next_step['skills_to_learn'])}")
                    print(f"Success Criteria: {next_step['success_criteria']}\n")
                    
                    proceed = input("Ready to start this step? (y/n): ").strip().lower()
                    if proceed == 'y':
                        # Regenerate actions for this step
                        action_result = orch.action_agent.generate_actions(user_id)
                        if action_result["status"] == "success":
                            print("\nNew action plan generated!")
                else:
                    print("You have completed all steps! Congratulations!")
        
        elif choice == "3":
            # Display full roadmap with reasoning
            path = context.get("active_path", {})
            if path.get("primary_path"):
                print_section("COMPLETE ROADMAP WITH REASONING")
                print(f"\nPath Rationale: {path.get('path_rationale', 'N/A')}\n")
                
                for step in path["primary_path"]["steps"]:
                    print(f"\nStep {step['step_number']}: {step['title']}")
                    print(f"  Description: {step.get('description', 'N/A')}")
                    print(f"  Duration: {step['duration_weeks']} weeks")
                    print(f"  Difficulty: {step.get('difficulty', 'N/A')}")
                    print(f"  Why this step: Builds foundation for ML engineering")
            
            return
        
        return
    
    print("PENDING ACTIONS:")
    for i, action in enumerate(actions[:5], 1):
        print(f"{i}. {action['title']} ({action['priority']} priority)")
        print(f"   Reasoning: {action.get('description', 'N/A')}")
    
    choice = input("\nSelect action number to mark complete (or 0 to skip): ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(actions):
            selected = actions[idx]
            
            hours = input(f"Hours spent on '{selected['title']}': ").strip()
            try:
                hours_float = float(hours)
            except ValueError:
                hours_float = None
            
            notes = input("Notes (optional): ").strip()
            
            result = orch.complete_action(
                user_id=user_id,
                action_id=selected["action_id"],
                time_spent_hours=hours_float,
                notes=notes
            )
            
            if result["status"] == "success":
                print("\nAction marked complete!")
                
                # Run feedback evaluation
                feedback_result = orch.evaluate_and_feedback(user_id)
                if feedback_result["status"] == "success":
                    feedback = feedback_result["feedback_analysis"]
                    print(f"\nProgress Update:")
                    print(f"   Overall: {feedback['overall_progress_rating']}")
                    print(f"   Velocity: {feedback['velocity_assessment']}")
                    print(f"   Confidence: {feedback['updated_confidence_score']:.2f}")
                    print(f"   Reasoning: {feedback.get('learning_insights', [{}])[0].get('insight', 'Keep going!')}")
                    print(f"\n{feedback['encouragement_message']}")
                    
                    # Check if rerouting needed after this action
                    updated_context = orch.get_student_context(user_id)
                    new_confidence = updated_context["readiness"].get("confidence_score", 0.5)
                    
                    if new_confidence < 0.4:
                        print("\nNote: Your confidence score has dropped.")
                        suggest_reroute = input("Would you like to review alternative paths? (y/n): ").strip().lower()
                        if suggest_reroute == 'y':
                            orch.handle_failure_and_reroute(user_id)
    
    except ValueError:
        pass


def main_menu():
    os.environ["GROQ_API_KEY"] = "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"
    """Main menu"""
    print_header("AGENTIC CAREER NAVIGATION SYSTEM")
    
    print("1. New Student Onboarding")
    print("2. Track Progress (existing student)")
    print("3. Load Context & View Status")
    print("4. Exit")
    
    choice = input("\nSelect option: ").strip()
    
    if choice == "1":
        result = interactive_onboarding()
        if result:
            user_id, orch = result
            
            track = input("\nTrack progress now? (y/n): ").strip().lower()
            if track == 'y':
                interactive_progress_tracking(user_id, orch)
    
    elif choice == "2":
        user_id = input("Enter user ID: ").strip()
        orch = Orchestrator()
        interactive_progress_tracking(user_id, orch)
    
    elif choice == "3":
        user_id = input("Enter user ID: ").strip()
        orch = Orchestrator()
        context = orch.get_student_context(user_id)
        print(json.dumps(context, indent=2))
    
    elif choice == "4":
        print("\nGoodbye!")
        return
    
    # Loop back to menu
    cont = input("\n\nReturn to main menu? (y/n): ").strip().lower()
    if cont == 'y':
        main_menu()


if __name__ == "__main__":
    main_menu()