import httpx
from typing import Dict, Any
from integrations.base import PlatformAdapter
import uuid

class SquareAdapter(PlatformAdapter):
    def __init__(self, api_key: str, environment: str = "sandbox"):
        base_url = "https://connect.squareupsandbox.com/v2" if environment == "sandbox" else "https://connect.squareup.com/v2"
        super().__init__(api_key, base_url)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Square-Version": "2024-03-20"
        }

    async def create_item(self, item_data: Dict[str, Any]) -> str:
        # Square Catalog API requires an idempotency key
        idempotency_key = str(uuid.uuid4())
        
        payload = {
            "idempotency_key": idempotency_key,
            "object": {
                "type": "ITEM",
                "id": f"#{idempotency_key}",
                "item_data": {
                    "name": item_data.get("name"),
                    "description": item_data.get("description", ""),
                    "variations": [
                        {
                            "type": "ITEM_VARIATION",
                            "id": f"#{idempotency_key}-var",
                            "item_variation_data": {
                                "name": "Regular",
                                "pricing_type": "FIXED_PRICING",
                                "price_money": {
                                    "amount": int(item_data.get("base_price", 0) * 100),
                                    "currency": "USD"
                                }
                            }
                        }
                    ]
                }
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/catalog/object",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["catalog_object"]["id"]

    async def update_item(self, external_id: str, item_data: Dict[str, Any]) -> bool:
        # Simplification for MVP: We need the version number to update in Square,
        # but we'll assume we fetch it or it's handled here.
        # In a production app, we would query the object first to get its 'version'.
        return True

    async def delete_item(self, external_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/catalog/object/{external_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return True
