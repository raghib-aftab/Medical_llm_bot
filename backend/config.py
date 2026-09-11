from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    mongodb_url: str
    database_name: str
    
    # LLM Settings
    llm_api_url: str
    llm_api_key: str
    llm_model: str
    
    # JWT Settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    
    # Email Settings
    gmail_user: str
    gmail_pass: str
    
    class Config:
        env_file = ".env"

settings = Settings()
