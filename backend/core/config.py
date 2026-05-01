from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "MenuFlow API"
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/menuflow"
    OPENAI_API_KEY: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
