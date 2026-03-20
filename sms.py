"""
Twilio SMS helper — sends OTP via real SMS.
Credentials are loaded from .env file.
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID  = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN   = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')


def send_otp_sms(to_phone: str, otp: str) -> dict:
    """
    Send OTP via Twilio SMS.
    Returns dict: { 'success': bool, 'sid': str or None, 'error': str or None }
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        return {
            'success': False,
            'sid': None,
            'error': 'Twilio credentials not configured in .env file'
        }

    if TWILIO_PHONE_NUMBER == '+1XXXXXXXXXX':
        return {
            'success': False,
            'sid': None,
            'error': 'TWILIO_PHONE_NUMBER not set in .env — please add your Twilio number'
        }

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=(
                f"🔐 Threat Reporting System\n"
                f"Your OTP is: {otp}\n"
                f"Valid for 5 minutes. Do NOT share this with anyone."
            ),
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )
        return {'success': True, 'sid': message.sid, 'error': None}

    except Exception as e:
        error_msg = str(e)
        # Provide helpful messages for common Twilio errors
        if '21608' in error_msg:
            error_msg = (
                "Trial account restriction: The number is not verified. "
                "Go to console.twilio.com → Verified Caller IDs and verify this number first."
            )
        elif '21211' in error_msg:
            error_msg = "Invalid phone number format. Use E.164 format like +919876543210"
        elif '20003' in error_msg:
            error_msg = "Authentication failed. Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env"
        return {'success': False, 'sid': None, 'error': error_msg}
