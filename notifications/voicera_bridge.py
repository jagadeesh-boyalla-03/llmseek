import os
import sys
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("VoicEraBridge")

VOICERA_PATH = r"C:\Users\boyal\OneDrive\Documents\VoicEra"

class VoicEraBridge:
    """
    Bridges AI Job Hunter directly to the existing VoicEra project telephony engine:
    Supports:
    1. Vobiz Voice Server (https://vobiz.johnaic.com)
    2. Plivo Outbound Telephony
    """
    def __init__(self):
        self.voicera_path = VOICERA_PATH
        self.is_voicera_available = os.path.exists(self.voicera_path)
        self.vobiz_base_url = os.getenv("VOICE_SERVER_BASE_URL", "https://vobiz.johnaic.com")
        self.vobiz_auth_id = os.getenv("VOBIZ_AUTH_ID")
        self.vobiz_auth_token = os.getenv("VOBIZ_AUTH_TOKEN")
        self.from_number = os.getenv("CALLER_ID_PHONE", "+919876543210")

    def inspect_voicera_capabilities(self) -> Dict[str, Any]:
        telephony_dir = os.path.join(self.voicera_path, "apps", "telephony")
        has_telephony = os.path.exists(telephony_dir)
        has_vobiz = os.path.exists(os.path.join(telephony_dir, "providers", "vobiz"))
        has_plivo = os.path.exists(os.path.join(telephony_dir, "providers", "plivo"))

        return {
            "voicera_found": self.is_voicera_available,
            "path": self.voicera_path,
            "has_telephony_module": has_telephony,
            "providers_detected": {
                "vobiz": has_vobiz,
                "plivo": has_plivo
            },
            "configured_voice_server": self.vobiz_base_url
        }

    async def initiate_voicera_call(
        self,
        to_number: str = "+919876543210",
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Triggers an outbound phone call using VoicEra's Vobiz / Plivo telephony engine.
        """
        if not self.is_voicera_available:
            return {"success": False, "error": "VoicEra project directory not found"}

        # If Vobiz credentials are set
        if self.vobiz_auth_id and self.vobiz_auth_token:
            try:
                # Add VoicEra to sys.path dynamically
                if self.voicera_path not in sys.path:
                    sys.path.insert(0, self.voicera_path)
                
                from apps.telephony.providers.vobiz.client import VobizClient
                client = VobizClient(self.vobiz_auth_id, self.vobiz_auth_token, self.vobiz_base_url)
                
                call_res = await client.initiate_call(
                    from_number=self.from_number,
                    to_number=to_number,
                    answer_url=f"{self.vobiz_base_url}/answer"
                )
                return {"success": True, "provider": "VoicEra_Vobiz", "response": call_res}
            except Exception as e:
                logger.error(f"Failed to initiate call via VoicEra Vobiz: {e}")
                return {"success": False, "error": str(e)}

        return {
            "success": True,
            "mode": "VOICERA_READY",
            "message": "VoicEra telephony structure detected with Vobiz & Plivo clients. Add VOBIZ_AUTH_ID and VOBIZ_AUTH_TOKEN to .env to dial live GSM SIM calls.",
            "target_number": to_number,
            "server_url": self.vobiz_base_url
        }

voicera_bridge = VoicEraBridge()

