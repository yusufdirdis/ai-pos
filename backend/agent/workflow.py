import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from db.models import MenuItem
from agent.ai_client import AIClient

SYSTEM_PROMPT = """
You are an AI assistant for a restaurant POS menu management system.
Your job is to help the user add, update, or remove menu items.

CRITICAL RULES FOR CREATE:
- To add a new item, you MUST have ALL of the following: name, price, and description.
- If the user provides a name but is MISSING the price OR description, you MUST ask for the missing information. Do NOT guess or invent a price. Do NOT create the item with missing fields.
- If an image is attached, you can use it to help write the description, but you still need the user to confirm the price.
- When asking for missing info, use action "CLARIFY".
- You can ONLY process ONE action at a time. If the user asks for multiple actions (like "remove all items"), return a CLARIFY action asking them to specify one item or do it one by one.

You MUST respond with ONLY a single valid JSON object. No extra text. Do NOT return an array.

For CREATE (only when you have name + price + description):
{
  "action": "CREATE",
  "name": "Extracted item name",
  "description": "Appetizing description of the item",
  "base_price": 10.99,
  "target_platforms": ["square", "ubereats"]
}

For UPDATE (user wants to change an existing item):
{
  "action": "UPDATE",
  "id": 1,
  "name": "Updated name if requested",
  "description": "Updated description if requested",
  "base_price": 12.99
}

For DELETE (user wants to remove an item):
{
  "action": "DELETE",
  "id": 1
}

For CLARIFY (missing required info, unclear request, or need confirmation):
{
  "action": "CLARIFY",
  "message": "I can add '10 Wing Dinner' to the menu! I just need a few more details:\\n- What price should it be listed at?\\n- Would you like to add a description?\\n- Would you like to attach a photo?"
}

IMPORTANT: Always use CLARIFY if the user only gives a name without a price. Never assume a price.
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

    def extract_structured_data(self, user_input: str, context: List[Dict[str, Any]], image_base64: str = None, history: str = "") -> Dict[str, Any]:
        # Build the prompt with conversation history for multi-turn context
        prompt_parts = []
        if history:
            prompt_parts.append(f"Previous conversation:\n{history}")
        prompt_parts.append(f"Current user message: {user_input}")
        prompt_parts.append(f"Existing menu items: {json.dumps(context)}")
        
        content_arr = [
            {"type": "text", "text": "\n\n".join(prompt_parts)}
        ]

        if image_base64:
            content_arr.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
            })

        raw = self.ai.chat(SYSTEM_PROMPT, content_arr, response_format_json=True)
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                if len(parsed) > 0:
                    return parsed[0]
                else:
                    return {"action": "CLARIFY", "message": "Could you clarify what you'd like to do?"}
            return parsed
        except json.JSONDecodeError:
            return {"action": "CLARIFY", "message": "I had trouble understanding that. Could you rephrase?"}
    def process_request(self, restaurant_id: int, user_input: str, image_base64: str = None, history: str = "") -> Dict[str, Any]:
        context = self.retrieve_context(restaurant_id, user_input)
        structured_data = self.extract_structured_data(user_input, context, image_base64, history)

        action = structured_data.get("action", "CLARIFY").upper()
        if action == "CLARIFY":
            return {"status": "clarify", "message": structured_data.get("message", "Could you provide more details?")}

        return {"status": "success", "action": action, "data": structured_data}
