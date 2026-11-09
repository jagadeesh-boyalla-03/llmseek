import json
import logging
import httpx
from typing import Dict, Any, List, Optional
from backend.config import settings

logger = logging.getLogger("OllamaEngine")

class OllamaClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.default_model = settings.DEFAULT_MODEL

    def is_service_running(self) -> bool:
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def list_installed_models(self) -> List[str]:
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models = res.json().get("models", [])
                    return [m.get("name") for m in models if "name" in m]
        except Exception as e:
            logger.warning(f"Could not reach Ollama at {self.base_url}: {e}")
        return ["llama3.2:3b", "qwen2.5:3b", "mistral:7b"] # Fallback known list

    def generate_completion(self, prompt: str, model: Optional[str] = None, system: Optional[str] = None) -> Optional[str]:
        target_model = model or self.default_model
        try:
            with httpx.Client(timeout=30.0) as client:
                payload = {
                    "model": target_model,
                    "prompt": prompt,
                    "stream": False
                }
                if system:
                    payload["system"] = system
                res = client.post(f"{self.base_url}/api/generate", json=payload)
                if res.status_code == 200:
                    return res.json().get("response")
        except Exception as e:
            logger.info(f"Ollama local inference unavailable, falling back to deterministic reasoning: {e}")
        return None

    def generate_structured_json(self, prompt: str, schema_description: str, model: Optional[str] = None) -> Optional[Dict[str, Any]]:
        system = f"You are a strict JSON generator. Return only a valid JSON object matching this schema: {schema_description}. Do not include markdown or explanations."
        response = self.generate_completion(prompt=prompt, model=model, system=system)
        if response:
            try:
                # Clean any markdown fences if present
                clean = response.strip()
                if clean.startswith("```json"):
                    clean = clean[7:]
                if clean.startswith("```"):
                    clean = clean[3:]
                if clean.endswith("```"):
                    clean = clean[:-3]
                return json.loads(clean.strip())
            except Exception as e:
                logger.warning(f"Failed to parse LLM JSON output: {e}")
        return None

ollama_client = OllamaClient()

