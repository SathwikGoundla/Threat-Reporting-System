#!/bin/bash
echo "================================================"
echo "  Threat Reporting System - Setup"
echo "================================================"

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python3 -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True); nltk.download('punkt_tab', quiet=True)"

echo ""
echo "================================================"
echo "  Setup Complete!"
echo ""
echo "  NEXT STEP: Edit .env and set TWILIO_PHONE_NUMBER"
echo "  (Get it from console.twilio.com → Active Numbers)"
echo ""
echo "  Then run:  python3 app.py"
echo "  Open:      http://localhost:5000"
echo "================================================"
