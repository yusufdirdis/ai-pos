"""
Uber Eats Platform Adapter
===========================
MODE SWITCHING:
  - Set UBEREATS_MODE=mock in .env for local dev (uses realistic fake data)
  - Set UBEREATS_MODE=live  in .env when you have real API credentials

When you receive your Uber Eats API credentials, add these to .env:
  UBEREATS_CLIENT_ID=your_client_id
  UBEREATS_CLIENT_SECRET=your_client_secret
  UBEREATS_STORE_ID=your_store_id
  UBEREATS_MODE=live
"""

import os
import logging
import httpx
import time
import uuid
from typing import Dict, Any, List
from .base import BaseAdapter

logger = logging.getLogger(__name__)


# ─── Realistic Mock Data ─────────────────────────────────────────────
# This mirrors the exact shape of a real Uber Eats menu response
# so the rest of the system is already wired to handle real data.
MOCK_MENU = {
    "menus": [{
        "id": "menu-main",
        "title": {"translations": {"en": "Main Menu"}},
        "categories": [
            {
                "id": "cat-appetizers",
                "title": {"translations": {"en": "Appetizers"}},
                "items": [
                    {
                        "id": "ue-item-001",
                        "title": {"translations": {"en": "Mozzarella Sticks"}},
                        "description": {"translations": {"en": "Hand-breaded mozzarella with marinara"}},
                        "price_info": {"price": 899, "currency_code": "USD"},
                        "image_url": "",
                        "modifier_groups": [],
                        "suspension_info": {"status": "ACTIVE"}
                    },
                    {
                        "id": "ue-item-002",
                        "title": {"translations": {"en": "Loaded Nachos"}},
                        "description": {"translations": {"en": "Tortilla chips with cheese, jalapeños, sour cream"}},
                        "price_info": {"price": 1199, "currency_code": "USD"},
                        "image_url": "",
                        "modifier_groups": [],
                        "suspension_info": {"status": "ACTIVE"}
                    }
                ]
            },
            {
                "id": "cat-entrees",
                "title": {"translations": {"en": "Entrees"}},
                "items": [
                    {
                        "id": "ue-item-003",
                        "title": {"translations": {"en": "Classic Cheeseburger"}},
                        "description": {"translations": {"en": "1/3 lb patty, American cheese, lettuce, tomato, house sauce"}},
                        "price_info": {"price": 1399, "currency_code": "USD"},
                        "image_url": "",
                        "modifier_groups": [],
                        "suspension_info": {"status": "ACTIVE"}
                    },
                    {
                        "id": "ue-item-004",
                        "title": {"translations": {"en": "Grilled Chicken Wrap"}},
                        "description": {"translations": {"en": "Grilled chicken, mixed greens, ranch, flour tortilla"}},
                        "price_info": {"price": 1249, "currency_code": "USD"},
                        "image_url": "",
                        "modifier_groups": [],
                        "suspension_info": {"status": "ACTIVE"}
                    },
                    {
                        "id": "ue-item-005",
                        "title": {"translations": {"en": "Fish & Chips"}},
                        "description": {"translations": {"en": "Beer-battered cod, seasoned fries, tartar sauce"}},
                        "price_info": {"price": 1549, "currency_code": "USD"},
                        "image_url": "",
                        "modifier_groups": [],
                        "suspension_info": {"status": "ACTIVE"}
                    }
                ]
            },
            {
                "id": "cat-drinks",
                "title": {"translations": {"en": "Drinks"}},
                "items": [
                    {
                        "id": "ue-item-006",
                        "title": {"translations": {"en": "Fresh Lemonade"}},
                        "description": {"translations": {"en": "House-made lemonade with mint"}},
                        "price_info": {"price": 499, "currency_code": "USD"},
                        "image_url": "",
                        "modifier_groups": [],
                        "suspension_info": {"status": "ACTIVE"}
                    }
                ]
            }
        ]
    }]
}


class UberEatsAdapter(BaseAdapter):
    """
    Uber Eats Menu API adapter.
    
    Supports two modes:
      - mock: Returns realistic fake data (for development before API approval)
      - live: Calls the real Uber Eats API with OAuth2 authentication
    """
    
    def __init__(self, credentials_arn: str):
        super().__init__(credentials_arn)
        self.mode = os.getenv("UBEREATS_MODE", "mock")
        self.client_id = os.getenv("UBEREATS_CLIENT_ID", "")
        self.client_secret = os.getenv("UBEREATS_CLIENT_SECRET", "")
        self.store_id = os.getenv("UBEREATS_STORE_ID", "")
        self.base_url = "https://api.uber.com/v2/eats"
        self.access_token = None
        self.token_expiry = 0
        
        logger.info(f"UberEatsAdapter initialized in [{self.mode}] mode")

    # ─── OAuth2 ───────────────────────────────────────────────────────
    def _ensure_token(self):
        """Fetch or refresh the OAuth2 token for the real API."""
        if self.mode == "mock":
            return
        
        if self.access_token and time.time() < self.token_expiry:
            return  # Token still valid
        
        logger.info("UberEats: Refreshing OAuth2 token...")
        response = httpx.post(
            "https://login.uber.com/oauth/v2/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
                "scope": "eats.store",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        data = response.json()
        self.access_token = data["access_token"]
        # Token lasts 30 days, but refresh a day early
        self.token_expiry = time.time() + data.get("expires_in", 2592000) - 86400
        logger.info("UberEats: OAuth2 token refreshed successfully.")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    # ─── PULL MENU ────────────────────────────────────────────────────
    def pull_menu(self, store_id: str = None) -> List[Dict[str, Any]]:
        """
        Pull the full menu from Uber Eats for a given store.
        Returns a flat list of items normalized to our internal format.
        
        Real API: GET /v2/eats/stores/{store_id}/menus
        """
        sid = store_id or self.store_id
        
        if self.mode == "mock":
            logger.info(f"UberEats [MOCK]: Pulling menu for store {sid}")
            raw_menu = MOCK_MENU
        else:
            self._ensure_token()
            logger.info(f"UberEats [LIVE]: GET /v2/eats/stores/{sid}/menus")
            response = httpx.get(
                f"{self.base_url}/stores/{sid}/menus",
                headers=self._headers(),
                timeout=30.0,
            )
            response.raise_for_status()
            raw_menu = response.json()
        
        # Normalize the Uber Eats nested structure into a flat item list
        return self._normalize_menu(raw_menu)

    def _normalize_menu(self, raw: dict) -> List[Dict[str, Any]]:
        """Convert Uber Eats nested menu JSON → flat list of our internal item format."""
        items = []
        for menu in raw.get("menus", []):
            for category in menu.get("categories", []):
                cat_name = category.get("title", {}).get("translations", {}).get("en", "Uncategorized")
                for item in category.get("items", []):
                    price_cents = item.get("price_info", {}).get("price", 0)
                    items.append({
                        "external_id": item["id"],
                        "name": item.get("title", {}).get("translations", {}).get("en", "Unknown"),
                        "description": item.get("description", {}).get("translations", {}).get("en", ""),
                        "base_price": round(price_cents / 100, 2),
                        "category": cat_name,
                        "image_url": item.get("image_url", ""),
                        "is_active": item.get("suspension_info", {}).get("status") == "ACTIVE",
                        "platform": "ubereats",
                    })
        return items

    # ─── CREATE ITEM ──────────────────────────────────────────────────
    def create_item(self, item_data: Dict[str, Any]) -> str:
        """
        Add a new item to the Uber Eats menu.
        
        Strategy: Uber Eats uses full-menu PUT for initial upload, then
        individual POST for sparse updates. For CREATE, we do a sparse 
        POST with a new item ID.
        
        Real API: POST /v2/eats/stores/{store_id}/menus/items/{item_id}
        """
        if self.mode == "mock":
            ext_id = f"ue-item-{item_data.get('id', uuid.uuid4().hex[:8])}"
            logger.info(f"UberEats [MOCK]: Created item → {ext_id}")
            return ext_id
        
        self._ensure_token()
        new_item_id = f"ue-{uuid.uuid4().hex[:12]}"
        payload = {
            "title": {"translations": {"en": item_data.get("name", "")}},
            "description": {"translations": {"en": item_data.get("description", "")}},
            "price_info": {
                "price": int(float(item_data.get("base_price", 0)) * 100),
                "currency_code": "USD",
            },
            "suspension_info": {"status": "ACTIVE"},
        }
        
        response = httpx.post(
            f"{self.base_url}/stores/{self.store_id}/menus/items/{new_item_id}",
            headers=self._headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        logger.info(f"UberEats [LIVE]: Created item → {new_item_id}")
        return new_item_id

    # ─── UPDATE ITEM ──────────────────────────────────────────────────
    def update_item(self, external_id: str, item_data: Dict[str, Any]) -> bool:
        """
        Update an existing item on Uber Eats (sparse update).
        
        Real API: POST /v2/eats/stores/{store_id}/menus/items/{item_id}
        """
        if self.mode == "mock":
            logger.info(f"UberEats [MOCK]: Updated item {external_id}")
            return True
        
        self._ensure_token()
        payload = {}
        if "name" in item_data:
            payload["title"] = {"translations": {"en": item_data["name"]}}
        if "description" in item_data:
            payload["description"] = {"translations": {"en": item_data["description"]}}
        if "base_price" in item_data:
            payload["price_info"] = {
                "price": int(float(item_data["base_price"]) * 100),
                "currency_code": "USD",
            }
        
        response = httpx.post(
            f"{self.base_url}/stores/{self.store_id}/menus/items/{external_id}",
            headers=self._headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        logger.info(f"UberEats [LIVE]: Updated item {external_id}")
        return True

    # ─── DELETE ITEM ──────────────────────────────────────────────────
    def delete_item(self, external_id: str) -> bool:
        """
        Delete an item from Uber Eats.
        
        Uber Eats doesn't have a DELETE endpoint — you remove items by
        uploading the full menu without them (PUT). For the sparse approach,
        we suspend the item instead.
        
        Real API: POST /v2/eats/stores/{store_id}/menus/items/{item_id}
                  with suspension_info.status = "SUSPENDED"
        """
        if self.mode == "mock":
            logger.info(f"UberEats [MOCK]: Deleted (suspended) item {external_id}")
            return True
        
        self._ensure_token()
        payload = {"suspension_info": {"status": "SUSPENDED"}}
        
        response = httpx.post(
            f"{self.base_url}/stores/{self.store_id}/menus/items/{external_id}",
            headers=self._headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        logger.info(f"UberEats [LIVE]: Suspended item {external_id}")
        return True
