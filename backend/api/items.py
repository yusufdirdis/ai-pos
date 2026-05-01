from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.session import get_db
from agent.agent import run_agent

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_with_agent(request: ChatRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    result = await run_agent(db, request.message, background_tasks)
    return {"reply": result}

@router.get("/")
def get_items(db: Session = Depends(get_db)):
    # Placeholder for CRUD logic
    return []

@router.post("/")
def create_item(db: Session = Depends(get_db)):
    # Placeholder for CRUD logic
    return {"status": "created"}
