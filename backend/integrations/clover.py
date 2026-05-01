import httpx
from typing import Dict, Any
from integrations.base import PlatformAdapter

class CloverAdapter(PlatformAdapter):
    def __init__(self, api_key: str, merchant_id: str, environment: str = "sandbox"):
        base_url = "https://sandbox.dev.clover.com/v3" if environment == "sandbox" else "https://api.clover.com/v3"
        super().__init__(api_key, base_url)
        self.merchant_id = merchant_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def create_item(self, item_data: Dict[str, Any]) -> str:
        payload = {
            "name": item_data.get("name"),
            "price": int(item_data.get("base_price", 0) * 100), # Clover expects cents
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/merchants/{self.merchant_id}/items",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data["id"]

    async def update_item(self, external_id: str, item_data: Dict[str, Any]) -> bool:
        payload = {
            "name": item_data.get("name"),
            "price": int(item_data.get("base_price", 0) * 100),
        }
        async with httpx.AsyncClient() as client:
            response = await client.post( # Clover uses POST to update items too
                f"{self.base_url}/merchants/{self.merchant_id}/items/{external_id}",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return True

    async def delete_item(self, external_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/merchants/{self.merchant_id}/items/{external_id}?delete=true",
                headers=self.headers
            )
            response.raise_for_status()
            return True
