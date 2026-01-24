# Career Navigation System - Start with 3 API Keys
# Simply run this script to start the application with all 3 API keys

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Career Navigation System - Starting with 3 API Keys" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Set API Keys
$env:GROQ_API_KEY_1 = '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'
$env:GROQ_API_KEY_2 = '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'
$env:GROQ_API_KEY_3 = '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'

Write-Host "API Keys Configured:" -ForegroundColor Green
Write-Host "  ✓ Key #1: gsk_GcbeJS0pPbcoWPW2...poO4OHbaI0" -ForegroundColor Cyan
Write-Host "  ✓ Key #2: gsk_CAQ2YnLjF0PrQSvO...5veaVZfbDZ" -ForegroundColor Cyan
Write-Host "  ✓ Key #3: gsk_eceeCDcVvnRYcjBU...P00weLjlcj" -ForegroundColor Cyan
Write-Host ""

Write-Host "Starting Streamlit..." -ForegroundColor Green
Write-Host "Open your browser at: " -ForegroundColor Yellow -NoNewline
Write-Host "http://localhost:8502" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

python -m streamlit run frontend/app.py
