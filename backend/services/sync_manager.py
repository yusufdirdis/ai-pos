import logging
from sqlalchemy.orm import Session
from db.models import SyncJob, SyncLog, PlatformConnection, PlatformItemMapping
from core.adapters.square import SquareAdapter
from core.adapters.ubereats import UberEatsAdapter
from core.adapters.doordash import DoorDashAdapter
from core.adapters.grubhub import GrubhubAdapter

logger = logging.getLogger(__name__)

class SyncManager:
    def __init__(self, db: Session):
        self.db = db

    def get_adapter(self, platform_name: str, credentials_arn: str):
        name = platform_name.lower().replace(" ", "")
        if name == 'square':
            return SquareAdapter(credentials_arn)
        elif name == 'ubereats':
            return UberEatsAdapter(credentials_arn)
        elif name == 'doordash':
            return DoorDashAdapter(credentials_arn)
        elif name == 'grubhub':
            return GrubhubAdapter(credentials_arn)
        raise ValueError(f"Unsupported platform: {platform_name}")

    def sync_item(self, sync_job_id: int, restaurant_id: int, menu_item: dict, action: str, target_platforms: list = None):
        """
        Executes a sync job for a specific menu item across all connected platforms.
        """
        job = self.db.query(SyncJob).filter(SyncJob.id == sync_job_id).first()
        if not job:
            return

        job.status = "in_progress"
        self.db.commit()

        connections = self.db.query(PlatformConnection).filter(
            PlatformConnection.restaurant_id == restaurant_id,
            PlatformConnection.is_active == True
        ).all()
        
        if target_platforms:
            target_platforms_lower = [p.lower().replace(" ", "") for p in target_platforms]
            # e.g. 'uber eats' -> 'ubereats'
            connections = [c for c in connections if c.platform_name.lower() in target_platforms_lower]

        for conn in connections:
            try:
                adapter = self.get_adapter(conn.platform_name, conn.credentials_secret_arn)
                mapping = self.db.query(PlatformItemMapping).filter(
                    PlatformItemMapping.menu_item_id == menu_item['id'],
                    PlatformItemMapping.platform_name == conn.platform_name
                ).first()


                external_id = mapping.external_item_id if mapping else None

                if action == "CREATE":
                    external_id = adapter.create_item(menu_item)
                    if not mapping:
                        mapping = PlatformItemMapping(
                            menu_item_id=menu_item['id'],
                            platform_name=conn.platform_name,
                            external_item_id=external_id,
                            last_sync_status="success"
                        )
                        self.db.add(mapping)
                    else:
                        mapping.external_item_id = external_id
                        mapping.last_sync_status = "success"

                elif action == "UPDATE" and external_id:
                    adapter.update_item(external_id, menu_item)
                    mapping.last_sync_status = "success"

                elif action == "DELETE" and external_id:
                    adapter.delete_item(external_id)
                    mapping.last_sync_status = "success"

                log = SyncLog(
                    sync_job_id=job.id,
                    platform_name=conn.platform_name,
                    action=action,
                    status="success"
                )
                self.db.add(log)

            except Exception as e:
                logger.error(f"Sync failed for {conn.platform_name}: {str(e)}")
                if mapping:
                    mapping.last_sync_status = "failed"
                log = SyncLog(
                    sync_job_id=job.id,
                    platform_name=conn.platform_name,
                    action=action,
                    status="failed",
                    error_message=str(e)
                )
                self.db.add(log)

        job.status = "completed"
        self.db.commit()
