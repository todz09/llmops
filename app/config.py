from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    groq_api_key: str
    model_name: str = "llama-3.1-8b-instant"
    max_tokens: int = 512
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()