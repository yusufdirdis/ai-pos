from fastapi import FastAPI
from api import items

app = FastAPI(title="MenuFlow API", description="AI POS and Delivery Integration")

app.include_router(items.router, prefix="/api/items", tags=["items"])

@app.get("/health")
def health_check():
    return {"status": "ok"}
