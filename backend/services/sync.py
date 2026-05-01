import asyncio
from sqlalchemy.orm import Session
from db.models import PlatformConnection, MenuItem, PlatformItemMapping
from integrations.square import SquareAdapter
from integrations.clover import CloverAdapter

async def sync_menu_item_to_platforms(db: Session, item: MenuItem):
    # Fetch all active connections for this restaurant
    connections = db.query(PlatformConnection).filter(
        PlatformConnection.restaurant_id == item.restaurant_id,
        PlatformConnection.status == 'active'
    ).all()

    for conn in connections:
        adapter = None
        if conn.platform_name == 'square':
            adapter = SquareAdapter(api_key=conn.encrypted_credentials)
        elif conn.platform_name == 'clover':
            # Simplified: Assuming encrypted_credentials holds a JSON with api_key and merchant_id
            import json
            creds = json.loads(conn.encrypted_credentials)
            adapter = CloverAdapter(api_key=creds['api_key'], merchant_id=creds['merchant_id'])
            
        if adapter:
            item_data = {
                "name": item.name,
                "description": item.description,
                "base_price": item.base_price
            }
            
            try:
                # 1. Check if mapping exists
                mapping = db.query(PlatformItemMapping).filter(
                    PlatformItemMapping.menu_item_id == item.id,
                    PlatformItemMapping.platform_connection_id == conn.id
                ).first()
                
                if mapping:
                    # Update
                    await adapter.update_item(mapping.external_item_id, item_data)
                else:
                    # Create
                    external_id = await adapter.create_item(item_data)
                    new_mapping = PlatformItemMapping(
                        menu_item_id=item.id,
                        platform_connection_id=conn.id,
                        external_item_id=external_id
                    )
                    db.add(new_mapping)
                    db.commit()
            except Exception as e:
                # In production, we log this to sync_logs
                print(f"Failed to sync to {conn.platform_name}: {e}")
