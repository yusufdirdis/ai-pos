"""
DoorDash Platform Adapter
==========================
MODE SWITCHING:
  - Set DOORDASH_MODE=mock in .env for local dev (uses realistic fake data)
  - Set DOORDASH_MODE=live  in .env when you have real API credentials

When you receive your DoorDash API credentials, add these to .env:
  DOORDASH_CLIENT_ID=your_client_id
  DOORDASH_CLIENT_SECRET=your_client_secret
  DOORDASH_STORE_ID=your_store_id
  DOORDASH_MODE=live
"""

import os
import logging
import httpx
import time
import uuid
import jwt
from typing import Dict, Any, List
from .base import BaseAdapter

logger = logging.getLogger(__name__)


# ─── Realistic Mock Data ─────────────────────────────────────────────
MOCK_MENU = {
    "store_id": "mock-dd-store-001",
    "menus": [{
        "id": "dd-menu-main",
        "name": "Main Menu",
        "categories": [
            {
                "id": "dd-cat-popular",
                "name": "Most Popular",
                "items": [
                    {
                        "id": "dd-item-001",
                        "name": "BBQ Bacon Burger",
                        "description": "Angus beef patty, smoked bacon, cheddar, BBQ sauce, onion rings",
                        "price": 1499,
                        "image_url": "",
                        "active": True,
                    },
                    {
                        "id": "dd-item-002",
                        "name": "Crispy Chicken Tenders",
                        "description": "Hand-breaded tenders with honey mustard and ranch",
                        "price": 1099,
                        "image_url": "",
                        "active": True,
                    },
                ]
            },
            {
                "id": "dd-cat-sides",
                "name": "Sides",
                "items": [
                    {
                        "id": "dd-item-003",
                        "name": "Loaded Fries",
                        "description": "Seasoned fries with cheese sauce, bacon bits, green onion",
                        "price": 799,
                        "image_url": "",
                        "active": True,
                    },
                    {
                        "id": "dd-item-004",
                        "name": "Onion Rings",
                        "description": "Beer-battered onion rings with chipotle aioli",
                        "price": 699,
                        "image_url": "",
                        "active": True,
                    },
                ]
            },
            {
                "id": "dd-cat-drinks",
                "name": "Beverages",
                "items": [
                    {
                        "id": "dd-item-005",
                        "name": "Strawberry Milkshake",
                        "description": "Hand-spun milkshake with real strawberries and whipped cream",
                        "price": 649,
                        "image_url": "",
                        "active": True,
                    },
                ]
            },
        ]
    }]
}


class DoorDashAdapter(BaseAdapter):
    """
    DoorDash Menu API adapter.
    
    Supports two modes:
      - mock: Returns realistic fake data (for development before certification)
      - live: Calls the real DoorDash API with JWT authentication
    """
    
    def __init__(self, credentials_arn: str):
        super().__init__(credentials_arn)
        self.mode = os.getenv("DOORDASH_MODE", "mock")
        self.client_id = os.getenv("DOORDASH_CLIENT_ID", "")
        self.client_secret = os.getenv("DOORDASH_CLIENT_SECRET", "")
        self.store_id = os.getenv("DOORDASH_STORE_ID", "")
        self.base_url = "https://openapi.doordash.com"
        self.access_token = None
        self.token_expiry = 0
        
        logger.info(f"DoorDashAdapter initialized in [{self.mode}] mode")

    # ─── JWT Auth ─────────────────────────────────────────────────────
    def _ensure_token(self):
        """Generate a JWT for the real DoorDash API."""
        if self.mode == "mock":
            return
        
        if self.access_token and time.time() < self.token_expiry:
            return
        
        logger.info("DoorDash: Generating JWT token...")
        token_payload = {
            "aud": "doordash",
            "iss": self.client_id,
            "kid": self.client_id,
            "exp": int(time.time()) + 300,  # 5 minutes
            "iat": int(time.time()),
        }
        self.access_token = jwt.encode(
            token_payload, 
            self.client_secret, 
            algorithm="HS256",
            headers={"dd-ver": "DD-JWT-V1"}
        )
        self.token_expiry = time.time() + 240  # Refresh before expiry
        logger.info("DoorDash: JWT token generated.")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    # ─── PULL MENU ────────────────────────────────────────────────────
    def pull_menu(self, store_id: str = None) -> List[Dict[str, Any]]:
        """
        Pull the full menu from DoorDash.
        Real API: GET /api/v1/stores/{store_id}/menus
        """
        sid = store_id or self.store_id
        
        if self.mode == "mock":
            logger.info(f"DoorDash [MOCK]: Pulling menu for store {sid}")
            raw_menu = MOCK_MENU
        else:
            self._ensure_token()
            logger.info(f"DoorDash [LIVE]: GET /api/v1/stores/{sid}/menus")
            response = httpx.get(
                f"{self.base_url}/api/v1/stores/{sid}/menus",
                headers=self._headers(),
                timeout=30.0,
            )
            response.raise_for_status()
            raw_menu = response.json()
        
        return self._normalize_menu(raw_menu)

    def _normalize_menu(self, raw: dict) -> List[Dict[str, Any]]:
        """Convert DoorDash menu JSON → flat list of our internal item format."""
        items = []
        for menu in raw.get("menus", []):
            for category in menu.get("categories", []):
                cat_name = category.get("name", "Uncategorized")
                for item in category.get("items", []):
                    price_cents = item.get("price", 0)
                    items.append({
                        "external_id": item["id"],
                        "name": item.get("name", "Unknown"),
                        "description": item.get("description", ""),
                        "base_price": round(price_cents / 100, 2),
                        "category": cat_name,
                        "image_url": item.get("image_url", ""),
                        "is_active": item.get("active", True),
                        "platform": "doordash",
                    })
        return items

    # ─── CREATE ITEM ──────────────────────────────────────────────────
    def create_item(self, item_data: Dict[str, Any]) -> str:
        """
        Add a new item to DoorDash menu.
        Real API: POST /api/v1/stores/{store_id}/menus/items
        """
        if self.mode == "mock":
            ext_id = f"dd-item-{item_data.get('id', uuid.uuid4().hex[:8])}"
            logger.info(f"DoorDash [MOCK]: Created item → {ext_id}")
            return ext_id
        
        self._ensure_token()
        payload = {
            "name": item_data.get("name", ""),
            "description": item_data.get("description", ""),
            "price": int(float(item_data.get("base_price", 0)) * 100),
            "active": True,
        }
        
        response = httpx.post(
            f"{self.base_url}/api/v1/stores/{self.store_id}/menus/items",
            headers=self._headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        ext_id = data.get("id", f"dd-{uuid.uuid4().hex[:12]}")
        logger.info(f"DoorDash [LIVE]: Created item → {ext_id}")
        return ext_id

    # ─── UPDATE ITEM ──────────────────────────────────────────────────
    def update_item(self, external_id: str, item_data: Dict[str, Any]) -> bool:
        """
        Update an existing item on DoorDash.
        Real API: PATCH /api/v1/stores/{store_id}/menus/items/{item_id}
        """
        if self.mode == "mock":
            logger.info(f"DoorDash [MOCK]: Updated item {external_id}")
            return True
        
        self._ensure_token()
        payload = {}
        if "name" in item_data:
            payload["name"] = item_data["name"]
        if "description" in item_data:
            payload["description"] = item_data["description"]
        if "base_price" in item_data:
            payload["price"] = int(float(item_data["base_price"]) * 100)
        
        response = httpx.patch(
            f"{self.base_url}/api/v1/stores/{self.store_id}/menus/items/{external_id}",
            headers=self._headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        logger.info(f"DoorDash [LIVE]: Updated item {external_id}")
        return True

    # ─── DELETE ITEM ──────────────────────────────────────────────────
    def delete_item(self, external_id: str) -> bool:
        """
        Delete (deactivate) an item on DoorDash.
        Real API: PATCH /api/v1/stores/{store_id}/menus/items/{item_id}/availability
        """
        if self.mode == "mock":
            logger.info(f"DoorDash [MOCK]: Deactivated item {external_id}")
            return True
        
        self._ensure_token()
        payload = {"active": False}
        
        response = httpx.patch(
            f"{self.base_url}/api/v1/stores/{self.store_id}/menus/items/{external_id}/availability",
            headers=self._headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        logger.info(f"DoorDash [LIVE]: Deactivated item {external_id}")
        return True
