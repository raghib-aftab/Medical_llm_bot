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

    # Email Settings (Resend - HTTP API, works on Render free tier)
    resend_api_key: str = ""
    resend_from_email: str = "onboarding@resend.dev"

    # Email Settings (Legacy Gmail SMTP - kept for reference)
    gmail_user: str = ""
    gmail_pass: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env


settings = Settings()