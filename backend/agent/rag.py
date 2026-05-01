from sqlalchemy.orm import Session
from agent.llm import client
from db.models import MenuItem

def generate_embedding(text_input: str) -> list[float]:
    response = client.embeddings.create(
        input=text_input,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def search_menu_items(db: Session, query: str, limit: int = 5):
    query_embedding = generate_embedding(query)
    
    # Cosine distance search with pgvector (<=>)
    items = db.query(MenuItem).order_by(
        MenuItem.embedding.cosine_distance(query_embedding)
    ).limit(limit).all()
    
    return items
