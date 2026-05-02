"""
AI Client Factory - supports Ollama (local/free), Gemini (cheapest cloud), OpenAI (fallback)
Switch providers by setting AI_PROVIDER in .env
"""
import json
import httpx
import os
from typing import List, Dict, Any

class AIClient:
    def __init__(self):
        from core.config import settings
        self.provider = settings.AI_PROVIDER.lower()
        self.settings = settings

    def chat(self, system_prompt: str, user_content: List[Dict], response_format_json: bool = True) -> str:
        if self.provider == "ollama":
            return self._ollama_chat(system_prompt, user_content)
        elif self.provider == "gemini":
            return self._gemini_chat(system_prompt, user_content)
        else:
            return self._openai_chat(system_prompt, user_content, response_format_json)

    def embed(self, text: str) -> List[float]:
        if self.provider == "ollama":
            return self._ollama_embed(text)
        elif self.provider == "gemini":
            # Gemini embedding
            return self._gemini_embed(text)
        else:
            return self._openai_embed(text)

    # ─── Ollama (Free, Local) ───────────────────────────────────────────────────

    def _ollama_chat(self, system_prompt: str, user_content: List[Dict]) -> str:
        text_parts = [p["text"] for p in user_content if p.get("type") == "text"]
        images = [p["image_url"]["url"].split(",")[1] for p in user_content if p.get("type") == "image_url"]

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text_parts[0] if text_parts else ""}
        ]

        payload = {
            "model": self.settings.OLLAMA_MODEL,
            "messages": messages,
            "stream": False,
            "format": "json",
            "keep_alive": -1
        }

        if images:
            payload["messages"][-1]["images"] = images

        try:
            with httpx.Client(timeout=120) as client:
                response = client.post(f"{self.settings.OLLAMA_BASE_URL}/api/chat", json=payload)
                response.raise_for_status()
                return response.json()["message"]["content"]
        except httpx.ConnectError:
            raise RuntimeError(
                "Ollama is not running. Start it with: ollama serve\n"
                "Or install it from: https://ollama.com/download"
            )

    def _ollama_embed(self, text: str) -> List[float]:
        payload = {"model": self.settings.OLLAMA_EMBED_MODEL, "input": text, "keep_alive": -1}
        try:
            with httpx.Client(timeout=30) as client:
                response = client.post(f"{self.settings.OLLAMA_BASE_URL}/api/embed", json=payload)
                response.raise_for_status()
                return response.json()["embeddings"][0]
        except httpx.ConnectError:
            raise RuntimeError("Ollama is not running. Run: ollama serve")

    # ─── Google Gemini (Cheapest Cloud, Free Tier) ─────────────────────────────

    def _gemini_chat(self, system_prompt: str, user_content: List[Dict]) -> str:
        import google.generativeai as genai
        genai.configure(api_key=self.settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            system_instruction=system_prompt
        )

        parts = []
        for item in user_content:
            if item.get("type") == "text":
                parts.append(item["text"])
            elif item.get("type") == "image_url":
                import base64
                b64 = item["image_url"]["url"].split(",")[1]
                parts.append({"mime_type": "image/jpeg", "data": base64.b64decode(b64)})

        response = model.generate_content(
            parts,
            generation_config={"response_mime_type": "application/json"}
        )
        return response.text

    def _gemini_embed(self, text: str) -> List[float]:
        import google.generativeai as genai
        genai.configure(api_key=self.settings.GEMINI_API_KEY)
        result = genai.embed_content(model="models/text-embedding-004", content=text)
        return result["embedding"]

    # ─── OpenAI (Fallback) ─────────────────────────────────────────────────────

    def _openai_chat(self, system_prompt: str, user_content: List[Dict], json_format: bool) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=self.settings.OPENAI_API_KEY)
        kwargs = {"model": "gpt-4o", "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ]}
        if json_format:
            kwargs["response_format"] = {"type": "json_object"}
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    def _openai_embed(self, text: str) -> List[float]:
        from openai import OpenAI
        client = OpenAI(api_key=self.settings.OPENAI_API_KEY)
        response = client.embeddings.create(model="text-embedding-3-small", input=text)
        return response.data[0].embedding
