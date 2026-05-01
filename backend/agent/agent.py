import json
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from agent.llm import client
from agent.rag import search_menu_items
from agent.tools import get_tools_schema
from services.sync import sync_menu_item_to_platforms
from db.models import MenuItem

async def run_agent(db: Session, user_message: str, background_tasks: BackgroundTasks) -> str:
    # 1. Retrieve Context
    similar_items = search_menu_items(db, user_message, limit=3)
    context_str = "Existing Menu Items Context:\n"
    for item in similar_items:
        context_str += f"- ID: {item.id}, Name: {item.name}, Price: {item.base_price}\n"
    
    # 2. Setup Messages
    messages = [
        {"role": "system", "content": "You are a helpful POS menu management assistant. You take natural language requests and use tools to manage the database. Use the provided context to find item IDs."},
        {"role": "user", "content": f"{context_str}\nUser Request: {user_message}"}
    ]
    
    # 3. Call LLM
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=get_tools_schema(),
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    
    # 4. Handle Tool Calls
    if response_message.tool_calls:
        tool_call = response_message.tool_calls[0]
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        
        # Mock database insertion
        if func_name == "create_menu_item":
            new_item = MenuItem(
                name=func_args.get("name"),
                base_price=func_args.get("base_price"),
                description=func_args.get("description", ""),
                restaurant_id=1  # Hardcoded for MVP
            )
            # In a real app we'd also generate embeddings here for pgvector
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            
            # Queue background task to sync to Square/Clover
            background_tasks.add_task(sync_menu_item_to_platforms, db, new_item)
            
            return f"Created menu item '{new_item.name}' and scheduled sync to POS platforms."
            
        elif func_name == "update_menu_item":
            item = db.query(MenuItem).filter(MenuItem.id == func_args.get("item_id")).first()
            if item:
                if "base_price" in func_args:
                    item.base_price = func_args["base_price"]
                db.commit()
                # Queue background task
                background_tasks.add_task(sync_menu_item_to_platforms, db, item)
                return f"Updated menu item '{item.name}' and scheduled sync to POS platforms."
                
        return f"Executed {func_name} with args {func_args}"
        
    return response_message.content or "No action taken."
