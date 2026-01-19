from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn

class Settings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        url = self.DATABASE_URL
        if url and url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        if url and url.startswith("postgresql://") and "asyncpg" not in url:
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url and "sslmode=require" in url:
             url = url.replace("sslmode=require", "ssl=require")
        if url and "channel_binding=require" in url:
             url = url.replace("channel_binding=require", "")
             # Clean up potential double && or trailing/leading ?&
             url = url.replace("?&", "?").replace("&&", "&")
             if url.endswith("?") or url.endswith("&"):
                 url = url[:-1]
        return url

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
