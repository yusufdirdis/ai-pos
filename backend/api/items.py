from fastapi import APIRouter, Depends, BackgroundTasks, File, UploadFile, Form, Query
from sqlalchemy import func
from pydantic import BaseModel
from sqlalchemy.orm import Session
import base64
from db.session import get_db
from agent.agent import run_agent

router = APIRouter()

@router.post("/chat")
async def chat_with_agent(
    background_tasks: BackgroundTasks,
    message: str = Form(...),
    platform_filter: str = Form(None),
    history: str = Form(""),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    image_base64 = None
    if image:
        contents = await image.read()
        # Pass the raw image directly to Gemini (it handles sizing natively)
        image_base64 = base64.b64encode(contents).decode('utf-8')
    try:
        result = await run_agent(db, message, image_base64, background_tasks, history)
        return {"reply": result}
    except RuntimeError as e:
        # These are our own descriptive errors (e.g. Ollama not running)
        return {"reply": f"⚠️ {str(e)}"}
    except Exception as e:
        error_msg = str(e)
        return {"reply": f"⚠️ Backend error: {error_msg}"}

from db.models import MenuItem, PlatformItemMapping

@router.get("/menu")
def get_menu(platform: str = None, db: Session = Depends(get_db)):
    restaurant_id = 1
    
    query = db.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    if platform:
        # We need to join with PlatformItemMapping if we strictly want only items on that platform
        query = query.join(PlatformItemMapping).filter(func.lower(PlatformItemMapping.platform_name) == platform.lower())
        
    items = query.order_by(MenuItem.id.desc()).limit(20).all()
    result = []
    for item in items:
        mappings = db.query(PlatformItemMapping).filter_by(menu_item_id=item.id).all()
        platforms = [m.platform_name.capitalize() for m in mappings if m.last_sync_status == 'success']
        status = "Synced" if platforms else "Pending"
        
        # If there are failed mappings, we show "Failed"
        if any(m.last_sync_status == 'failed' for m in mappings):
            status = "Failed"
            
        result.append({
            "id": item.id,
            "name": item.name,
            "price": f"${item.base_price:.2f}",
            "status": status,
            "platforms": platforms,
            "image": item.image_url
        })
    return result


@router.post("/pull-menu")
def pull_menu_from_platform(platform: str = Form("ubereats"), db: Session = Depends(get_db)):
    """
    Pull the full menu from an external platform (Uber Eats, etc.) 
    and import all items into our central database.
    """
    from core.adapters.ubereats import UberEatsAdapter
    from agent.workflow import AgentWorkflow
    
    restaurant_id = 1  # MVP hardcoded
    
    if platform.lower() == "ubereats":
        adapter = UberEatsAdapter(credentials_arn="env")
    else:
        return {"error": f"Platform '{platform}' not yet supported for pull"}
    
    # Pull the menu from the platform
    external_items = adapter.pull_menu()
    
    workflow = AgentWorkflow(db)
    imported = 0
    skipped = 0
    
    for ext_item in external_items:
        # Check if we already have this item mapped
        existing_mapping = db.query(PlatformItemMapping).filter_by(
            platform_name=platform.lower(),
            external_item_id=ext_item["external_id"]
        ).first()
        
        if existing_mapping:
            # Item already imported — update it
            item = db.query(MenuItem).filter_by(id=existing_mapping.menu_item_id).first()
            if item:
                item.name = ext_item["name"]
                item.description = ext_item["description"]
                item.base_price = ext_item["base_price"]
                if ext_item.get("image_url"):
                    item.image_url = ext_item["image_url"]
                skipped += 1
            continue
        
        # Create new item in our DB
        embedding = workflow.embed_text(f"{ext_item['name']} {ext_item['description']}")
        new_item = MenuItem(
            restaurant_id=restaurant_id,
            name=ext_item["name"],
            description=ext_item["description"],
            base_price=ext_item["base_price"],
            image_url=ext_item.get("image_url") or None,
            embedding=embedding,
            is_active=ext_item.get("is_active", True),
        )
        db.add(new_item)
        db.flush()  # Get the ID
        
        # Create the platform mapping
        mapping = PlatformItemMapping(
            menu_item_id=new_item.id,
            platform_name=platform.lower(),
            external_item_id=ext_item["external_id"],
            last_sync_status="success",
        )
        db.add(mapping)
        imported += 1
    
    db.commit()
    return {
        "status": "success",
        "imported": imported,
        "updated": skipped,
        "total": len(external_items),
        "platform": platform,
    }


@router.get("/platforms")
def get_platforms():
    """Return available platforms and their current mode (mock/live)."""
    import os
    return {
        "platforms": [
            {
                "name": "ubereats",
                "display_name": "Uber Eats",
                "mode": os.getenv("UBEREATS_MODE", "mock"),
                "has_credentials": bool(os.getenv("UBEREATS_CLIENT_ID")),
            },
            {
                "name": "square",
                "display_name": "Square",
                "mode": "sandbox",
                "has_credentials": bool(os.getenv("SQUARE_SANDBOX_TOKEN")),
            },
        ]
    }
