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
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    image_base64 = None
    if image:
        contents = await image.read()
        
        # Optimize image for AI speed
        from io import BytesIO
        from PIL import Image
        img = Image.open(BytesIO(contents))
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Resize to max 512x512 to massively speed up Ollama Vision
        img.thumbnail((512, 512))
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        optimized_contents = buffer.getvalue()
        
        image_base64 = base64.b64encode(optimized_contents).decode('utf-8')
    try:
        # TODO: Pass platform_filter to run_agent to filter RAG context
        result = await run_agent(db, message, image_base64, background_tasks)
        return {"reply": result}
    except RuntimeError as e:
        # These are our own descriptive errors (e.g. Ollama not running)
        return {"reply": f"⚠️ {str(e)}"}
    except Exception as e:
        error_msg = str(e)
        if "insufficient_quota" in error_msg or "429" in error_msg:
            return {"reply": "⚠️ OpenAI quota exceeded. Switch to Ollama (free) by setting AI_PROVIDER=ollama in .env"}
        if "GEMINI_API_KEY" in error_msg or "API_KEY_INVALID" in error_msg:
            return {"reply": "⚠️ Invalid Gemini API key. Check your GEMINI_API_KEY in .env"}
        return {"reply": f"⚠️ Backend error: {error_msg[:200]}"}

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
