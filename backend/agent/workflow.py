import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from db.models import MenuItem
from agent.ai_client import AIClient

SYSTEM_PROMPT = """
You are an AI assistant for a restaurant POS system.
Extract the menu item details from the user's request.

You MUST respond with ONLY a valid JSON object.
For CREATE actions, use this exact structure:
{
  "action": "CREATE",
  "name": "Extracted item name",
  "description": "Mouth-watering item description based on text and image",
  "base_price": 10.99,
  "target_platforms": ["square", "ubereats"]
}

For UPDATE or DELETE actions, use this exact structure:
{
  "action": "UPDATE",
  "id": 1,
  "name": "Updated name if requested",
  "base_price": 12.99
}

If the user's request is unclear, use action "CLARIFY" and provide a "message" key.
"""

class AgentWorkflow:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.ai = AIClient()

    def embed_text(self, text: str) -> List[float]:
        return self.ai.embed(text)

    def retrieve_context(self, restaurant_id: int, query: str) -> List[Dict[str, Any]]:
        """Uses RAG to find similar items for this restaurant."""
        # If no items exist yet, skip the vector search (avoids NULL embedding errors)
        item_count = self.db.query(MenuItem).filter(
            MenuItem.restaurant_id == restaurant_id
        ).count()

        if item_count == 0:
            return []

        try:
            query_embedding = self.embed_text(query)
            similar_items = self.db.query(MenuItem).filter(
                MenuItem.restaurant_id == restaurant_id,
                MenuItem.embedding.isnot(None)
            ).order_by(
                MenuItem.embedding.cosine_distance(query_embedding)
            ).limit(5).all()

            return [
                {"id": item.id, "name": item.name, "description": item.description, "base_price": item.base_price}
                for item in similar_items
            ]
        except Exception:
            # If vector search fails, return empty context gracefully
            return []

    def extract_structured_data(self, user_input: str, context: List[Dict[str, Any]], image_base64: str = None) -> Dict[str, Any]:
        content_arr = [
            {"type": "text", "text": f"User Request: {user_input}\n\nExisting Menu Context: {json.dumps(context)}"}
        ]

        if image_base64:
            content_arr.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
            })

        raw = self.ai.chat(SYSTEM_PROMPT, content_arr, response_format_json=True)
        return json.loads(raw)

    def process_request(self, restaurant_id: int, user_input: str, image_base64: str = None) -> Dict[str, Any]:
        context = self.retrieve_context(restaurant_id, user_input)
        structured_data = self.extract_structured_data(user_input, context, image_base64)

        action = structured_data.get("action", "CLARIFY").upper()
        if action == "CLARIFY":
            return {"status": "clarify", "message": structured_data.get("message", "Could you provide more details?")}

        return {"status": "success", "action": action, "data": structured_data}
