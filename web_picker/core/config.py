from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приожения."""
    BOT_TOKEN: str
    BASE_WEBAPP_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="allow")


settings = Settings()
