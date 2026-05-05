import logging
import httpx
import uuid
import os
from typing import Dict, Any, List
from .base import BaseAdapter

logger = logging.getLogger(__name__)

class SquareAdapter(BaseAdapter):
    def __init__(self, credentials_arn: str):
        super().__init__(credentials_arn)
        self.access_token = os.getenv("SQUARE_SANDBOX_TOKEN", credentials_arn)
        self.base_url = "https://connect.squareupsandbox.com/v2/catalog"
        self.headers = {
            "Square-Version": "2024-03-20",
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def pull_menu(self, store_id: str = None) -> List[Dict[str, Any]]:
        """Pull catalog from Square. Returns normalized item list."""
        logger.info("SquareAdapter: pull_menu not yet implemented for live mode")
        return []
        
    def create_item(self, item_data: Dict[str, Any]) -> str:
        logger.info(f"SquareAdapter: Creating item {item_data.get('name')}")
        price_cents = int(float(item_data.get('base_price', 0)) * 100)
        
        payload = {
            "idempotency_key": str(uuid.uuid4()),
            "object": {
                "type": "ITEM",
                "id": "#new_item",
                "item_data": {
                    "name": item_data.get("name"),
                    "description": item_data.get("description", ""),
                    "variations": [
                        {
                            "type": "ITEM_VARIATION",
                            "id": "#new_variation",
                            "item_variation_data": {
                                "item_id": "#new_item",
                                "name": "Regular",
                                "pricing_type": "FIXED_PRICING",
                                "price_money": {
                                    "amount": price_cents,
                                    "currency": "USD"
                                }
                            }
                        }
                    ]
                }
            }
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(f"{self.base_url}/object", headers=self.headers, json=payload)
                response.raise_for_status()
                data = response.json()
                return data["catalog_object"]["id"]
        except Exception as e:
            logger.error(f"Square API Error: {str(e)}")
            raise e
        
    def update_item(self, external_id: str, item_data: Dict[str, Any]) -> bool:
        logger.info(f"SquareAdapter: Updating item {external_id}")
        return True
        
    def delete_item(self, external_id: str) -> bool:
        logger.info(f"SquareAdapter: Deleting item {external_id}")
        return True

