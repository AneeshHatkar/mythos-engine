from pydantic import BaseModel


class AppConfig(BaseModel):
    app_name: str = "MythOS Engine"
    app_version: str = "0.1.0"
    environment: str = "local"
    api_prefix: str = "/api"


settings = AppConfig()
