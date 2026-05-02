import logging
from typing import Dict, Any
from .base import BaseAdapter

logger = logging.getLogger(__name__)

class UberEatsAdapter(BaseAdapter):
    """
    Adapter for Uber Eats API.
    In MVP Phase 1/2, this mocks the actual HTTP calls to Uber Eats since
    partner approval is required for sandbox access.
    """
    
    def __init__(self, credentials_arn: str):
        super().__init__(credentials_arn)
        self.access_token = "mock-ubereats-token"
        self.base_url = "https://api.uber.com/v2/eats/stores"
        
    def create_item(self, item_data: Dict[str, Any]) -> str:
        logger.info(f"UberEatsAdapter: Creating item {item_data.get('name')}")
        # MOCK HTTP POST to Uber Eats API
        return f"ue-item-{item_data.get('id', 'new')}"
        
    def update_item(self, external_id: str, item_data: Dict[str, Any]) -> bool:
        logger.info(f"UberEatsAdapter: Updating item {external_id}")
        return True
        
    def delete_item(self, external_id: str) -> bool:
        logger.info(f"UberEatsAdapter: Deleting item {external_id}")
        return True
