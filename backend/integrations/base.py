from abc import ABC, abstractmethod
from typing import Dict, Any

class PlatformAdapter(ABC):
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
    async def create_item(self, item_data: Dict[str, Any]) -> str:
        """Create an item and return the external platform ID."""
        pass

    @abstractmethod
    async def update_item(self, external_id: str, item_data: Dict[str, Any]) -> bool:
        """Update an existing item on the platform."""
        pass

    @abstractmethod
    async def delete_item(self, external_id: str) -> bool:
        """Delete an item from the platform."""
        pass
