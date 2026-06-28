from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Flight Watch"
    client_id: str
    client_secret: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings



