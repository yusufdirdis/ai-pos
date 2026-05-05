import json
import os
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from agent.workflow import AgentWorkflow
from db.models import MenuItem, SyncJob, PlatformConnection
from services.sync_manager import SyncManager

def execute_agent_sync(db: Session, sync_job_id: int, restaurant_id: int, structured_data: dict):
    sync_manager = SyncManager(db)
    target_platforms = structured_data.get("target_platforms")
    sync_manager.sync_item(sync_job_id, restaurant_id, structured_data, structured_data.get("action", "CREATE"), target_platforms)

def ensure_platform_connections(db: Session, restaurant_id: int):
    # Ensure the restaurant row exists first (foreign key requirement)
    from db.models import Restaurant
    restaurant = db.query(Restaurant).filter_by(id=restaurant_id).first()
    if not restaurant:
        db.add(Restaurant(id=restaurant_id, name="My Restaurant"))
        db.commit()

    # Seed platform connections for the dashboard demo
    for platform in ["square", "ubereats"]:
        conn = db.query(PlatformConnection).filter_by(restaurant_id=restaurant_id, platform_name=platform).first()
        if not conn:
            db.add(PlatformConnection(restaurant_id=restaurant_id, platform_name=platform, credentials_secret_arn="mock", is_active=True))
    db.commit()

async def run_agent(db: Session, user_message: str, image_base64: str, background_tasks: BackgroundTasks, history: str = "") -> str:
    restaurant_id = 1  # Hardcoded for MVP
    ensure_platform_connections(db, restaurant_id)

    workflow = AgentWorkflow(db)
    result = workflow.process_request(restaurant_id, user_message, image_base64, history)
    
    if result["status"] == "clarify":
        return result["message"]
        
    action = result["action"]
    data = result["data"]
    
    if action == "CREATE":
        # 1. Create the item in our central database
        embedding = workflow.embed_text(f"{data.get('name')} {data.get('description')}")
        new_item = MenuItem(
            restaurant_id=restaurant_id,
            name=data.get("name", "Unnamed Item"),
            description=data.get("description", ""),
            base_price=float(data.get("base_price", 0.0) or 0.0),
            image_url=f"data:image/jpeg;base64,{image_base64}" if image_base64 else None,
            embedding=embedding
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        
        # 2. Add ID to data for sync
        data["id"] = new_item.id
        
        # 3. Create a SyncJob
        job = SyncJob(restaurant_id=restaurant_id, status="pending")
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # 4. Trigger Sync in Background
        background_tasks.add_task(execute_agent_sync, db, job.id, restaurant_id, data)
        return f"Got it! I added '{new_item.name}' to your menu and queued an update to your connected platforms."
        
    elif action == "UPDATE":
        item_id = data.get("id")
        if not item_id:
            return "I couldn't identify which item you wanted to update. Please specify the name."
            
        item = db.query(MenuItem).filter_by(id=item_id, restaurant_id=restaurant_id).first()
        if not item:
            return "I couldn't find that item in the database."
            
        if "name" in data and data["name"]: 
            item.name = data["name"]
        if "description" in data and data["description"]: 
            item.description = data["description"]
        if "base_price" in data: 
            item.base_price = float(data["base_price"])
        if image_base64: 
            item.image_url = f"data:image/jpeg;base64,{image_base64}"
            
        # Re-embed if text changed
        item.embedding = workflow.embed_text(f"{item.name} {item.description}")
        db.commit()
        
        job = SyncJob(restaurant_id=restaurant_id, status="pending")
        db.add(job)
        db.commit()
        db.refresh(job)
        
        data["id"] = item.id
        background_tasks.add_task(execute_agent_sync, db, job.id, restaurant_id, data)
        return f"Got it! I updated '{item.name}'."
        
    elif action == "DELETE":
        item_id = data.get("id")
        if not item_id:
            return "I couldn't identify which item you wanted to delete."
            
        item = db.query(MenuItem).filter_by(id=item_id, restaurant_id=restaurant_id).first()
        if not item:
            return "I couldn't find that item to delete."
            
        item_name = item.name
        # Must delete platform mappings first to avoid FK violation
        from db.models import PlatformItemMapping
        db.query(PlatformItemMapping).filter_by(menu_item_id=item_id).delete()
        db.delete(item)
        db.commit()
        
        job = SyncJob(restaurant_id=restaurant_id, status="pending")
        db.add(job)
        db.commit()
        db.refresh(job)
        
        data["id"] = item_id
        background_tasks.add_task(execute_agent_sync, db, job.id, restaurant_id, data)
        return f"Got it! I deleted '{item_name}' from your menu."
        
    return "I am not sure how to handle that request yet."

