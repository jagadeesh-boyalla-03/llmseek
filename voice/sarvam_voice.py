import os
import base64
import logging
import httpx
from typing import Dict, Any, Optional

logger = logging.getLogger("SarvamVoice")

class SarvamVoiceEngine:
    """
    Integrates Sarvam AI (India's premier Speech AI) with VoiceEra and AI Job Hunter.
    Provides natural Indian accent Text-to-Speech (bulbul:v1) and Speech-to-Text (saaras:v1).
    """
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY")
        self.tts_url = "https://api.sarvam.ai/text-to-speech"
        self.stt_url = "https://api.sarvam.ai/speech-to-text"

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def synthesize_speech(
        self,
        text: str,
        language_code: str = "en-IN", # en-IN, te-IN (Telugu), hi-IN (Hindi)
        speaker: str = "meera" # meera, arvind, kavya
    ) -> Optional[str]:
        """
        Synthesizes ultra-natural Indian voice using Sarvam AI bulbul:v1 model.
        Returns base64 encoded audio string ready for instant browser/phone playback.
        """
        if not self.api_key:
            logger.info("SARVAM_API_KEY not set. Using local TTS fallback.")
            return None

        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": [text],
            "target_language_code": language_code,
            "speaker": speaker,
            "pitch": 0,
            "pace": 1.05,
            "loudness": 1.5,
            "speech_sample_rate": 16000,
            "enable_preprocessing": True,
            "model": "bulbul:v1"
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.post(self.tts_url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    audios = data.get("audios", [])
                    if audios:
                        return audios[0] # Base64 audio string
        except Exception as e:
            logger.error(f"Sarvam AI TTS error: {e}")
        return None

sarvam_voice = SarvamVoiceEngine()

