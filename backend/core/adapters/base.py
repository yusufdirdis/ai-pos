from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAdapter(ABC):
    def __init__(self, credentials_arn: str):
        self.credentials_arn = credentials_arn
    
    @abstractmethod
    def pull_menu(self, store_id: str) -> List[Dict[str, Any]]:
        """Pull the full menu from the external platform. Returns list of item dicts."""
        pass

    @abstractmethod
    def create_item(self, item_data: Dict[str, Any]) -> str:
        """Create an item on the external platform and return its external ID."""
        pass
    
    @abstractmethod
    def update_item(self, external_id: str, item_data: Dict[str, Any]) -> bool:
        """Update an existing item on the external platform."""
        pass
    
    @abstractmethod
    def delete_item(self, external_id: str) -> bool:
        """Delete an item from the external platform."""
        pass
