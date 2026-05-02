from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    
    PROJECT_NAME: str = "MenuFlow API"
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/menuflow"
    
    # AI Provider: "openai" | "gemini" | "ollama"
    AI_PROVIDER: str = "ollama"
    
    # OpenAI (fallback)
    OPENAI_API_KEY: str = ""
    
    # Google Gemini (cheapest cloud option)
    GEMINI_API_KEY: str = ""
    
    # Ollama (free, local, runs on your Mac)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2-vision"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    
    # Square
    SQUARE_SANDBOX_TOKEN: str = ""

settings = Settings()
