@echo off
echo ================================================
echo   Threat Reporting System - Setup
echo ================================================

python -m venv venv
call venv\Scripts\activate.bat

pip install -r requirements.txt

python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('punkt_tab', quiet=True)"

echo.
echo ================================================
echo   Setup Complete!
echo.
echo   NEXT STEP: Open .env file and set your
echo   TWILIO_PHONE_NUMBER (from console.twilio.com)
echo.
echo   Then run:   python app.py
echo   Open:       http://localhost:5000
echo ================================================
pause
