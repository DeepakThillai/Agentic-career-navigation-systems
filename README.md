# Career Navigation System

A comprehensive AI-powered career guidance and planning system that helps students navigate their career paths with personalized roadmaps, step-based progression, AI-validated action completion, and intelligent rerouting.

## Features

### Core Capabilities

- **User Onboarding Wizard**: 3-step interactive process to gather student profile, skills, and career goals
- **Personalized Roadmap Generation**: AI-generated comprehensive roadmaps with 4-6 sequential steps
- **Step-Based Progression**: Each step contains 3 initial actions to complete
- **AI-Validated Action Completion**: 
  - 5 validation questions generated for each action
  - Student provides answers
  - AI calculates relevance score (0-1)
  - Action marked complete only when score >= 0.7
  - Can retry if score insufficient
- **Automatic Step Advancement**: When all actions in a step are satisfied, automatically move to next step
- **Interactive Dashboard**: 7-tab interface for complete lifecycle management
- **Real-time Feedback**: Progress analysis and recommendations after each action
- **Intelligent Rerouting**: Detect deviations and suggest alternative paths with user choice
- **Roadmap Restart After Rerouting**: Complete alternative path and redirect back to original target
- **Market Intelligence**: Real-time market analysis for target roles
- **Full Context Persistence**: All progress, scores, and history updated in user context

## Project Structure

```
career-navigation-system/
├── frontend/                  # Streamlit web application
│   ├── app.py                # Main dashboard (multi-page app)
│   ├── pages/                # Additional pages (extensible)
│   └── components/           # Reusable UI components
├── backend/                  # Core business logic
│   ├── orchestrator.py       # Meta-agent coordinator
│   ├── user_context.py       # Student context manager
│   └── agents/               # 8 specialized AI agents
│       ├── agent_student_profiling.py
│       ├── agent_goal_interpretation.py
│       ├── agent_readiness_assessment.py
│       ├── agent_market_intelligence.py
│       ├── agent_career_path_planning.py
│       ├── agent_action_recommendation.py
│       ├── agent_feedback_learning.py
│       └── agent_rerouting.py
├── data/                     # Data persistence
│   └── user_contexts/        # Student profile storage (JSON)
├── tests/                    # Testing and verification
├── main.py                   # Entry point
├── requirements.txt          # Python dependencies
├── run_frontend.bat          # Windows launcher for frontend
├── run_backend.bat           # Windows launcher for backend
└── README.md                 # This file
```

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Groq API Key (for LLM features)

### Installation

```bash
# Clone or download the project
cd career-navigation-system

# Install dependencies
pip install -r requirements.txt

# Set environment variables
set GROQ_API_KEY=your_api_key_here
```

### Running the System

#### Option 1: Using Windows Batch Scripts

```bash
# Run frontend (Streamlit app)
run_frontend.bat

# Run backend (API server)
run_backend.bat
```

#### Option 2: Manual Launch

```bash
# Frontend
streamlit run frontend/app.py

# Backend
python main.py
```

## Testing & Examples

### View New Flow Implementation
See IMPLEMENTATION_COMPLETE.txt for detailed summary of all changes.

### Run Test Suite
```bash
# Test new roadmap and step-based progression flow
python test_new_flow.py
```

### View Example Workflow
```bash
# See complete workflow example with all new features
python quickstart_example.py
```

## System Architecture
### 8 Specialized AI Agents

1. **Student Profiler**: Analyzes background, skills, experience, and learning capacity
2. **Goal Interpreter**: Understands career objectives and interprets into actionable roles
3. **Readiness Assessor**: Evaluates confidence level, preparedness, and deviation risks
4. **Market Analyst**: Provides market intelligence on demand, trends, and competition
5. **Path Planner**: Generates detailed learning roadmaps with steps and timelines
6. **Action Recommender**: Creates actionable tasks with priorities and success criteria
7. **Feedback Generator**: Analyzes progress and provides insights for course correction
8. **Rerouting Agent**: Suggests alternative paths when current path shows deviation

### Meta-Orchestrator

The **Orchestrator** coordinates all agents:
- Manages student context across all operations
- Calls agents in sequence or parallel as needed
- Maintains state and history
- Handles path changes and rerouting

### Context Management

The **UserContextManager** handles:
- Loading/saving student profiles (JSON files)
- Context persistence across sessions
- Export/import functionality
- Data validation and integrity

## User Journey

### 1. Home Page
- Select existing user or create new one
- Intuitive user discovery from data directory

### 2. Onboarding (3 Steps)
- **Step 1**: Basic information (experience, education, skills)
- **Step 2**: Background and projects (strengths, risks, motivation)
- **Step 3**: Timeline and goals (commitment, learning style, vision)
- System generates personalized career path

### 3. Interactive Dashboard (7 Tabs)

#### Overview Tab
- Key metrics (confidence score, market demand, success probability)
- Risk assessment and path status

#### Roadmap Tab
- Complete learning path with steps
- Difficulty levels and success criteria
- Skills to learn and resources

#### Actions Tab
- Mark actions complete with time tracking
- View pending and completed actions
- Interactive action management

#### Progress Tab
- Overall completion rate progress bar
- Hours spent tracking
- Blocker documentation

#### Feedback Tab
- Generate AI-powered progress analysis
- Strengths observed and areas of concern
- Recommended adjustments
- Confidence changes and motivation assessment

#### Rerouting Tab
- Path health check
- Analyze alternative routes when needed
- Switch paths with one click
- View rerouting history

#### Settings Tab
- Export context as JSON
- User information
- Navigation and logout

## Key Workflows

### Create New User
```
Home -> Enter User ID -> Step 1 (Basic Info) -> Step 2 (Background) -> Step 3 (Timeline) 
-> Generate Path -> Dashboard
```

### Complete an Action
```
Dashboard -> Actions Tab -> Select action -> Enter hours spent -> Add notes -> Mark Complete 
-> Context updates -> Feedback available
```

### Switch Career Path
```
Dashboard -> Rerouting Tab -> Analyze Alternatives -> Select Option -> Apply Path 
-> Context updates -> New roadmap displayed
```

### Get AI Feedback
```
Dashboard -> Feedback Tab -> Generate AI Feedback -> View analysis and recommendations
```

## API Reference

### Orchestrator Methods

```python
# Start student onboarding
result = orchestrator.onboard_student(user_id, onboarding_data)

# Get student context
context = orchestrator.get_student_context(user_id)

# Complete an action
result = orchestrator.complete_action(user_id, action_title, hours_spent, notes)

# Generate feedback
result = orchestrator.evaluate_and_feedback(user_id)

# Analyze rerouting options
result = orchestrator.handle_failure_and_reroute(user_id)

# Apply alternative path
result = orchestrator.apply_alternative_path(user_id, alternative, path_type)
```

### UserContextManager Methods

```python
# Load student context
context = manager.load_context(user_id)

# Save context
manager.save_context(user_id, context)

# Get full context
context = manager.get_full_context(user_id)

# Export context
json_data = manager.export_context(user_id)

# List all users
users = manager.list_all_users()
```

## Configuration

### Environment Variables

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### Streamlit Configuration

The app uses:
- **Layout**: Wide mode for better space utilization
- **Sidebar**: Expanded by default
- **Page Title**: Career Navigation System
- **Icon**: Career compass

## Data Format

### Student Context (JSON)

```json
{
  "user_id": "string",
  "created_at": "ISO-8601 timestamp",
  "last_updated": "ISO-8601 timestamp",
  "student_profile": {
    "experience_level": "string",
    "learning_capacity": "string",
    "technical_skills": {},
    "strength_areas": [],
    "weakness_areas": [],
    "risk_factors": []
  },
  "career_goals": {
    "current_goal": "string",
    "goal_clarity_score": "float",
    "commitment_level": "string",
    "interpreted_goal": {}
  },
  "readiness": {
    "confidence_score": "float",
    "readiness_verdict": "string",
    "deviation_risk": "string",
    "weak_areas": [],
    "diagnostic_questions": [],
    "diagnostic_answers": []
  },
  "market_context": {
    "target_role_analysis": {}
  },
  "active_path": {
    "target_role": "string",
    "primary_path": {},
    "success_probability": "float",
```
## Complete Workflow Guide

### Phase 1: Onboarding
1. User creates profile with education, skills, and career goal
2. System generates student profile, interprets goal, assesses readiness
3. Market intelligence gathered for target role
4. Career path is planned
5. **Roadmap is generated** with 4-6 sequential steps

### Phase 2: Step-Based Progression
**Each Step Flow:**
1. Student sees 3 initial actions in the current step
2. Student clicks to start an action
3. **5 validation questions** are automatically generated
4. Student provides detailed answers to all 5 questions
5. **AI Evaluation Phase:**
   - Agent analyzes answers against success criteria
   - Calculates relevance score (0.0 to 1.0)
   - Determines if understanding is sufficient
6. **Agent Satisfaction:**
   - If score >= 0.7: Action marked as COMPLETE
   - If score < 0.7: Action marked as NEEDS REVIEW
     - User can retry with feedback hints
7. **Step Completion:**
   - When all 3 actions in step are satisfied
   - System automatically advances to next step
   - Next 3 actions become available
8. **Roadmap Completion:**
   - User completes all steps sequentially
   - Final roadmap status: COMPLETE

**Context Updates:**
- User context updated after EACH action evaluation
- Stores: relevance_scores, agent_satisfied flag, attempt count
- Tracks: step completion percentage, current step number
- Records: completion timestamps for all actions

### Phase 3: Deviation & Rerouting
**When User Faces Challenges:**
1. User reports deviation reason (e.g., "Lost interest in target role")
2. System triggers detect_deviation_and_reroute()
3. **Alternative Generation:**
   - 2 alternative career paths suggested
   - Adjusted version of original path offered
   - Each option includes success probability and timeline
4. **User Choice:**
   - User selects one of 3 options
   - Selected alternative becomes new roadmap
   - New step-based progression begins
5. **After Alternative Completion:**
   - System detects alternative is complete
   - User is offered redirect back to original target
   - Can accept and return to original path

**Context Updates in Rerouting:**
- is_rerouting: True during rerouting
- alternative_roadmaps: All alternatives offered
- selected_alternative_id: User's choice
- active_path.target_role: Updated to new role
- active_path.current_path_type: Set to "rerouted"

## User Context Schema

### Roadmap Structure
```json
{
  "roadmap": {
    "roadmap_id": "unique_identifier",
    "total_steps": 5,
    "steps": [
      {
        "step_number": 1,
        "title": "Foundation Building",
        "description": "Build core fundamentals",
        "status": "in_progress|completed|pending",
        "completion_percentage": 0.67,
        "actions": [
          {
            "action_id": "action_1_1",
            "title": "Learn Python Basics",
            "description": "Master Python fundamentals",
            "success_criteria": "Complete 10 exercises with 80%+ accuracy",
            "status": "pending|in_progress|completed",
            "questions": [
              {"question": "...", "type": "conceptual|practical|..."}
            ],
            "user_answers": ["answer1", "answer2", ...],
            "relevance_score": 0.85,
            "agent_satisfied": true,
            "attempts": 1,
            "completion_timestamp": "2026-01-23T..."
          }
        ]
      }
    ],
    "current_step_number": 1,
    "completed_steps": [],
    "created_at": "2026-01-23T...",
    "status": "generated|in_progress|completed"
  }
}
```

### Rerouting State
```json
{
  "reroute_state": {
    "is_rerouting": false,
    "original_roadmap_id": "roadmap_id",
    "alternative_roadmaps": [
      {
        "option_id": 1,
        "new_target_role": "Data Scientist",
        "reason": "Aligns with recent interests",
        "success_probability": 0.75,
        "timeline_months": 12
      }
    ],
    "selected_alternative_id": null,
    "alternative_completion_percentage": 0.0,
    "redirect_to_step": null,
    "reroute_timestamp": null,
    "reroute_reason": null
  }
}
```

## Extended API Reference

### Orchestrator Methods

#### Roadmap Generation
```python
result = orchestrator.generate_roadmap(user_id)
# Returns: {"status": "success", "roadmap": {...}, "message": "..."}
```

#### Action Completion
```python
# Step 1: Mark action as in-progress and generate questions
result = orchestrator.complete_action_in_roadmap(user_id, step_number, action_id)
# Returns: {"status": "success", "questions": [...], "action_id": "..."}

# Step 2: Submit answers for evaluation
result = orchestrator.submit_action_answers(user_id, step_number, action_id, answers_list)
# Returns: {
#   "status": "success",
#   "relevance_score": 0.85,
#   "agent_satisfied": true|false,
#   "feedback": "...",
#   "next_steps": "..."
# }
```

#### Roadmap Status
```python
result = orchestrator.get_roadmap_status(user_id)
# Returns: {
#   "current_step": 2,
#   "current_step_title": "Intermediate Skills",
#   "completed_steps": 1,
#   "total_steps": 5,
#   "progress_percentage": 33.3,
#   "pending_actions_in_current_step": [...],
#   "roadmap_status": "in_progress"
# }
```

#### Rerouting
```python
# Detect and generate alternatives
result = orchestrator.detect_deviation_and_reroute(user_id, deviation_reason)
# Returns: {
#   "alternatives": [...],
#   "adjusted_original": {...}
# }

# User selects option
result = orchestrator.select_reroute_option(user_id, option_id)
# option_id can be: 1, 2 (for alternatives) or "original_adjusted"

# Complete alternative and prepare for redirect
result = orchestrator.complete_rerouted_roadmap(user_id)
# Returns: {"status": "success", "redirect_available": true}
```

## Dashboard Interface

### Tab 1: Overview
- User profile summary
- Target role and goal clarity
- Current readiness assessment
- Quick statistics

### Tab 2: Roadmap
- Visual roadmap with all steps
- Step status indicators
- Action completion tracking
- Action start/complete buttons
- Overall progress bar

### Tab 3: Actions
- Current pending actions
- Completed actions history
- Time tracking
- Priority actions

### Tab 4: Progress
- Completion rates
- Time spent
- Step progression history
- Blockers encountered

### Tab 5: Feedback
- Progress analysis
- Strengths and areas for improvement
- Learning insights
- Recommendations

### Tab 6: Rerouting
- Current rerouting status
- Alternative options when triggered
- Selection buttons
- Redirect to original after completion

### Tab 7: Settings
- Export context
- Clear history
- System preferences

## Troubleshooting

### Issue: "No module named 'backend'"
- **Solution**: Ensure you're running from the project root directory
- **Solution**: Verify Python path includes parent directory

### Issue: Streamlit app won't start
- **Solution**: Check if Streamlit is installed: `pip install streamlit`
- **Solution**: Try: `python -m streamlit run frontend/app.py`

### Issue: Groq API errors
- **Solution**: Verify GROQ_API_KEY is set correctly
- **Solution**: Check API key has valid permissions
- **Solution**: Ensure internet connection is working

### Issue: Context not saving
- **Solution**: Check data/user_contexts/ directory exists and is writable
- **Solution**: Verify file permissions
- **Solution**: Check disk space

## Performance Optimization

- **Context Caching**: Contexts are cached in session state to avoid repeated file I/O
- **Agent Parallelization**: Multiple agents can run in parallel for speed
- **Lazy Loading**: Dashboard components load on demand

## Security Notes

- API keys should never be hardcoded; use environment variables
- Student contexts contain personal information; ensure proper access control
- Validate all user inputs before processing
- Use HTTPS for production deployments

## Future Enhancements

- Multi-user authentication system
- Role-based access control (mentors, admins)
- Integration with job marketplaces
- Mobile app support
- Advanced analytics dashboard
- Video coaching modules
- Peer mentoring network

## Support and Contribution

For issues, questions, or contributions:
1. Review this README for comprehensive documentation
2. Check the verify_structure.py for system validation
3. Examine agent implementations for specific functionality
4. Review main.py for orchestrator usage examples

## License

This project is provided as-is for educational and commercial use.

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Status**: Production Ready
