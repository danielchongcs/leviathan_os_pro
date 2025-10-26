@echo off
setlocal enabledelayedexpansion

REM === Path to your project ===
set "PROJECT=C:\Users\dan_y\Downloads\Compressed\leviathan_os_pro\leviathan_os_pro"

REM === Go to project folder ===
cd /d "%PROJECT%"

REM === Ensure the virtual environment exists ===
if not exist ".venv\Scripts\activate.bat" (
  echo [Setup] Creating virtual environment...
  python -m venv .venv
)

REM === Activate venv ===
call ".venv\Scripts\activate.bat"

REM === Install deps once (skips next runs) ===
if not exist ".venv\.deps_installed.flag" (
  echo [Setup] Installing requirements (first run only)...
  pip install --upgrade pip
  pip install -r requirements.txt
  pip install pylint flake8 bandit mypy black isort pandas-stubs types-requests
  echo done> ".venv\.deps_installed.flag"
)

REM === Launch the Streamlit app in a new window ===
start "Leviathan - App" cmd /k "cd /d \"%PROJECT%\" && .\.venv\Scripts\activate && streamlit run app.py"

REM === Launch the Auto Code Doctor PRO in a new window ===
start "Leviathan - Auto Code Check" cmd /k "cd /d \"%PROJECT%\" && .\.venv\Scripts\activate && python scripts\auto_code_check_pro.py"

echo.
echo ✅ Leviathan is launching. 
echo - App:     http://localhost:8501
echo - Reports: %PROJECT%\exports\code_reports
echo.
pause
