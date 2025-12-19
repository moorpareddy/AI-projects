# Resume Analyzer - Windows Startup Script
# This script starts both backend and frontend servers

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   Resume Analyzer & Job Matcher Startup    " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-Not (Test-Path .env)) {
    Write-Host "Warning: .env file not found" -ForegroundColor Yellow
    Write-Host "Copying .env.example to .env..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Created .env file" -ForegroundColor Green
    Write-Host "Please edit .env and add your API keys" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter after updating .env with your API keys"
}

# Check if virtual environment exists
if (-Not (Test-Path venv)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt | Out-Null

Write-Host ""
Write-Host "Starting servers..." -ForegroundColor Green
Write-Host ""

# Start backend in new window
Write-Host "Starting Backend API (FastAPI)..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & .\venv\Scripts\Activate.ps1
    python -m backend.main
}
Write-Host "   Backend Job ID: $($backendJob.Id)" -ForegroundColor Gray
Write-Host "   Backend URL: http://localhost:8000" -ForegroundColor Gray
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""

# Wait for backend to start
Write-Host "Waiting for backend to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start frontend in new window
Write-Host "Starting Frontend (Streamlit)..." -ForegroundColor Cyan
$frontendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & .\venv\Scripts\Activate.ps1
    streamlit run frontend/app.py
}
Write-Host "   Frontend Job ID: $($frontendJob.Id)" -ForegroundColor Gray
Write-Host "   Frontend URL: http://localhost:8501" -ForegroundColor Gray
Write-Host ""

Write-Host "=============================================" -ForegroundColor Green
Write-Host "          All Services Started!             " -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000           " -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs      " -ForegroundColor White
Write-Host "  Frontend: http://localhost:8501           " -ForegroundColor White
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend and Frontend are running in background jobs" -ForegroundColor Yellow
Write-Host "To view job status: Get-Job" -ForegroundColor Yellow
Write-Host "To view output: Receive-Job -Id (job id) -Keep" -ForegroundColor Yellow
Write-Host "To stop: Stop-Job -Id (job id)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Opening browser in 3 seconds..." -ForegroundColor Cyan
Start-Sleep -Seconds 3
Start-Process "http://localhost:8501"

Write-Host ""
Write-Host "Press Ctrl+C to stop monitoring (services will continue running)" -ForegroundColor Gray
Write-Host ""

# Monitor jobs
try {
    while ($true) {
        Start-Sleep -Seconds 5
        $backendState = (Get-Job -Id $backendJob.Id).State
        $frontendState = (Get-Job -Id $frontendJob.Id).State
        
        if ($backendState -ne "Running") {
            Write-Host "Backend job stopped with state: $backendState" -ForegroundColor Red
            Receive-Job -Id $backendJob.Id
            break
        }
        
        if ($frontendState -ne "Running") {
            Write-Host "Frontend job stopped with state: $frontendState" -ForegroundColor Red
            Receive-Job -Id $frontendJob.Id
            break
        }
    }
}
finally {
    Write-Host ""
    Write-Host "To stop services, run:" -ForegroundColor Yellow
    $backendId = $backendJob.Id
    $frontendId = $frontendJob.Id
    Write-Host "   Stop-Job -Id $backendId" -ForegroundColor Gray
    Write-Host "   Stop-Job -Id $frontendId" -ForegroundColor Gray
}
