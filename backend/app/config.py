from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    github_token: str

    fast_model: str = "claude-haiku-4-5-20251001"
    smart_model: str = "claude-sonnet-4-6"

    class Config:
        env_file = ".env"


settings = Settings()
