"""
Grubhub Platform Adapter
=========================
MODE SWITCHING:
  - Set GRUBHUB_MODE=mock in .env for local dev (uses realistic fake data)
  - Set GRUBHUB_MODE=live  in .env when you have real API credentials

When you receive your Grubhub API credentials, add these to .env:
  GRUBHUB_API_KEY=your_api_key
  GRUBHUB_STORE_ID=your_store_id
  GRUBHUB_MODE=live
"""

import os
import logging
import httpx
import uuid
from typing import Dict, Any, List
from .base import BaseAdapter

logger = logging.getLogger(__name__)


# ─── Realistic Mock Data ─────────────────────────────────────────────
MOCK_MENU = {
    "restaurant_id": "mock-gh-store-001",
    "menus": [{
        "menu_id": "gh-menu-main",
        "menu_name": "Full Menu",
        "menu_categories": [
            {
                "category_id": "gh-cat-bowls",
                "name": "Bowls",
                "menu_items": [
                    {
                        "item_id": "gh-item-001",
                        "name": "Teriyaki Chicken Bowl",
                        "description": "Grilled chicken, steamed rice, teriyaki glaze, sesame seeds, green onion",
                        "price": {"amount": 1349, "currency": "USD"},
                        "image_url": "",
                        "available": True,
                    },
                    {
                        "item_id": "gh-item-002",
                        "name": "Poke Bowl",
                        "description": "Fresh ahi tuna, sushi rice, avocado, edamame, sriracha mayo",
                        "price": {"amount": 1599, "currency": "USD"},
                        "image_url": "",
                        "available": True,
                    },
                ]
            },
            {
                "category_id": "gh-cat-wraps",
                "name": "Wraps & Sandwiches",
                "menu_items": [
                    {
                        "item_id": "gh-item-003",
                        "name": "Buffalo Chicken Wrap",
                        "description": "Crispy buffalo chicken, blue cheese crumbles, lettuce, tomato",
                        "price": {"amount": 1199, "currency": "USD"},
                        "image_url": "",
                        "available": True,
                    },
                    {
                        "item_id": "gh-item-004",
                        "name": "Philly Cheesesteak",
                        "description": "Shaved ribeye, provolone, sautéed peppers and onions, hoagie roll",
                        "price": {"amount": 1449, "currency": "USD"},
                        "image_url": "",
                        "available": True,
                    },
                ]
            },
            {
                "category_id": "gh-cat-desserts",
                "name": "Desserts",
                "menu_items": [
                    {
                        "item_id": "gh-item-005",
                        "name": "Churros",
                        "description": "Cinnamon sugar churros with chocolate dipping sauce",
                        "price": {"amount": 599, "currency": "USD"},
                        "image_url": "",
                        "available": True,
                    },
                ]
            },
        ]
    }]
}


class GrubhubAdapter(BaseAdapter):
    """
    Grubhub Menu API adapter.
    
    Supports two modes:
      - mock: Returns realistic fake data (for development before QA approval)
      - live: Calls the real Grubhub Partner API
    """
    
    def __init__(self, credentials_arn: str):
        super().__init__(credentials_arn)
        self.mode = os.getenv("GRUBHUB_MODE", "mock")
        self.api_key = os.getenv("GRUBHUB_API_KEY", "")
        self.store_id = os.getenv("GRUBHUB_STORE_ID", "")
        self.base_url = "https://api-partner.grubhub.com"
        
        logger.info(f"GrubhubAdapter initialized in [{self.mode}] mode")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    # ─── PULL MENU ────────────────────────────────────────────────────
    def pull_menu(self, store_id: str = None) -> List[Dict[str, Any]]:
        """
        Pull the full menu from Grubhub.
        Real API: GET /v1/restaurants/{restaurant_id}/menus
        """
        sid = store_id or self.store_id
        
        if self.mode == "mock":
            logger.info(f"Grubhub [MOCK]: Pulling menu for store {sid}")
            raw_menu = MOCK_MENU
        else:
            logger.info(f"Grubhub [LIVE]: GET /v1/restaurants/{sid}/menus")
            response = httpx.get(
                f"{self.base_url}/v1/restaurants/{sid}/menus",
                headers=self._headers(),
                timeout=30.0,
            )
            response.raise_for_status()
            raw_menu = response.json()
        
        return self._normalize_menu(raw_menu)

    def _normalize_menu(self, raw: dict) -> List[Dict[str, Any]]:
        """Convert Grubhub menu JSON → flat list of our internal item format."""
        items = []
        for menu in raw.get("menus", []):
            for category in menu.get("menu_categories", []):
                cat_name = category.get("name", "Uncategorized")
                for item in category.get("menu_items", []):
                    price_info = item.get("price", {})
                    price_cents = price_info.get("amount", 0) if isinstance(price_info, dict) else 0
                    items.append({
                        "external_id": item["item_id"],
                        "name": item.get("name", "Unknown"),
                        "description": item.get("description", ""),
                        "base_price": round(price_cents / 100, 2),
                        "category": cat_name,
                        "image_url": item.get("image_url", ""),
                        "is_active": item.get("available", True),
                        "platform": "grubhub",
                    })
        return items

    # ─── CREATE ITEM ──────────────────────────────────────────────────
    def create_item(self, item_data: Dict[str, Any]) -> str:
        """
        Add a new item to Grubhub menu.
        Real API: POST /v1/restaurants/{restaurant_id}/menus/items
        """
        if self.mode == "mock":
            ext_id = f"gh-item-{item_data.get('id', uuid.uuid4().hex[:8])}"
            logger.info(f"Grubhub [MOCK]: Created item → {ext_id}")
            return ext_id
        
        payload = {
            "name": item_data.get("name", ""),
            "description": item_data.get("description", ""),
            "price": {
                "amount": int(float(item_data.get("base_price", 0)) * 100),
                "currency": "USD",
            },
            "available": True,
        }
        
        response = httpx.post(
            f"{self.base_url}/v1/restaurants/{self.store_id}/menus/items",
            headers=self._headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        ext_id = data.get("item_id", f"gh-{uuid.uuid4().hex[:12]}")
        logger.info(f"Grubhub [LIVE]: Created item → {ext_id}")
        return ext_id

    # ─── UPDATE ITEM ──────────────────────────────────────────────────
    def update_item(self, external_id: str, item_data: Dict[str, Any]) -> bool:
        """
        Update an existing item on Grubhub.
        Real API: PUT /v1/restaurants/{restaurant_id}/menus/items/{item_id}
        """
        if self.mode == "mock":
            logger.info(f"Grubhub [MOCK]: Updated item {external_id}")
            return True
        
        payload = {}
        if "name" in item_data:
            payload["name"] = item_data["name"]
        if "description" in item_data:
            payload["description"] = item_data["description"]
        if "base_price" in item_data:
            payload["price"] = {
                "amount": int(float(item_data["base_price"]) * 100),
                "currency": "USD",
            }
        
        response = httpx.put(
            f"{self.base_url}/v1/restaurants/{self.store_id}/menus/items/{external_id}",
            headers=self._headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        logger.info(f"Grubhub [LIVE]: Updated item {external_id}")
        return True

    # ─── DELETE ITEM ──────────────────────────────────────────────────
    def delete_item(self, external_id: str) -> bool:
        """
        Delete (mark unavailable) an item on Grubhub.
        Real API: PUT /v1/restaurants/{restaurant_id}/menus/items/{item_id}
        """
        if self.mode == "mock":
            logger.info(f"Grubhub [MOCK]: Deactivated item {external_id}")
            return True
        
        payload = {"available": False}
        
        response = httpx.put(
            f"{self.base_url}/v1/restaurants/{self.store_id}/menus/items/{external_id}",
            headers=self._headers(),
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        logger.info(f"Grubhub [LIVE]: Deactivated item {external_id}")
        return True
