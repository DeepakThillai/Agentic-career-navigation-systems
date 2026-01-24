@echo off
REM Career Navigation System - Start with 3 API Keys
REM Simply run this file to start the application with all 3 API keys

setlocal enabledelayedexpansion

set GROQ_API_KEY_1=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
set GROQ_API_KEY_2=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
set GROQ_API_KEY_3=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

echo ============================================================
echo  Career Navigation System - Starting with 3 API Keys
echo ============================================================
echo.
echo API Keys Configured:
echo  • Key #1: gsk_GcbeJS0pPbcoWPW2...poO4OHbaI0
echo  • Key #2: gsk_CAQ2YnLjF0PrQSvO...5veaVZfbDZ
echo  • Key #3: gsk_eceeCDcVvnRYcjBU...P00weLjlcj
echo.
echo Starting Streamlit...
echo Open browser at: http://localhost:8502
echo.

cd /d %~dp0
python -m streamlit run frontend/app.py
