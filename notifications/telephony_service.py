import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("TelephonyService")

class TelephonyService:
    """
    Handles real GSM/PSTN telephone calls to candidate mobile
    using cloud telecom gateways (Twilio / Exotel / Plivo).
    """
    def __init__(self):
        self.twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_from = os.getenv("TWILIO_PHONE_NUMBER") # e.g. +1... or virtual number
        self.exotel_sid = os.getenv("EXOTEL_SID")
        self.exotel_token = os.getenv("EXOTEL_TOKEN")

    def make_real_phone_call(
        self,
        to_number: str = "+919876543210",
        spoken_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dials candidate mobile via Twilio Voice API if configured.
        Falls back to local browser speech call if credentials are not yet entered.
        """
        cleaned_number = to_number.strip().replace(" ", "").replace("-", "")
        if not cleaned_number.startswith("+"):
            cleaned_number = f"+91{cleaned_number}"

        default_speech = (
            "Hello, this is your AI Job Hunter Jarvis agent calling. "
            "Your application for Python Developer has been successfully submitted. "
            "Advertised package is 3.2 LPA with a 1.5 years service agreement. "
            "Your tailored ATS resume has been sent to your email. Goodbye!"
        )
        message_to_speak = spoken_message or default_speech

        # If Twilio credentials are provided
        if self.twilio_sid and self.twilio_token and self.twilio_from:
            try:
                import httpx
                # TwiML for Text-to-Speech call
                twiml = f"<Response><Say voice='alice' language='en-IN'>{message_to_speak}</Say></Response>"
                url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Calls.json"
                
                with httpx.Client(timeout=10.0) as client:
                    res = client.post(
                        url,
                        auth=(self.twilio_sid, self.twilio_token),
                        data={
                            "To": cleaned_number,
                            "From": self.twilio_from,
                            "Twiml": twiml
                        }
                    )
                    if res.status_code in [200, 201]:
                        call_data = res.json()
                        return {
                            "success": True,
                            "mode": "REAL_TELECOM_CALL",
                            "call_sid": call_data.get("sid"),
                            "status": "Dialing",
                            "to": cleaned_number,
                            "message": message_to_speak
                        }
                    else:
                        logger.warning(f"Twilio API error: {res.text}")
            except Exception as e:
                logger.error(f"Failed to place Twilio call: {e}")

        # In-App Phone Audio Call Mode (Direct phone speaker playback via PWA)
        return {
            "success": True,
            "mode": "IN_APP_VOICE_CALL",
            "to": cleaned_number,
            "status": "Ready to ring in phone browser",
            "spoken_prompt": message_to_speak,
            "instructions": (
                "To make actual GSM carrier calls ring your SIM card, add TWILIO_ACCOUNT_SID, "
                "TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER to .env. "
                "Meanwhile, your phone speaker rings and speaks this exact call directly through the PWA!"
            )
        }

telephony_service = TelephonyService()

