@echo off
setlocal
cd /d "%~dp0"
set "EVIDENCETRACE_ENABLE_LIVE=0"
set "EVIDENCETRACE_BUNDLE=%CD%\ui_artifacts\current"

set "NEEDS_INSTALL=0"
if not exist ".venv\Scripts\python.exe" (
  echo Creating .venv with the default Python launcher...
  py -3.10 -m venv .venv || goto :error
  set "NEEDS_INSTALL=1"
)

".venv\Scripts\python.exe" -c "import streamlit, pydantic, yaml, pandas, altair, requests" >nul 2>&1
if errorlevel 1 set "NEEDS_INSTALL=1"
if /I "%1"=="--install" set "NEEDS_INSTALL=1"
if "%NEEDS_INSTALL%"=="1" (
  echo Installing pinned dashboard dependencies...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip || goto :error
  ".venv\Scripts\python.exe" -m pip install -r requirements-runtime.txt || goto :error
)

if not exist "ui_artifacts\current\manifest.json" (
  echo Missing validated dashboard bundle: ui_artifacts\current\manifest.json
  goto :error
)

echo Starting EvidenceTrace offline at http://localhost:8501
".venv\Scripts\python.exe" scripts\run_research_ui.py --bundle ui_artifacts\current --port 8501
exit /b %errorlevel%

:error
echo Dashboard launch failed. Run: run_dashboard.bat --install
exit /b 1
