from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

import os
from pathlib import Path


class Settings(BaseSettings):
    # General
    app_name: str = "ClassifyApp"
    environment: str = "development"  # development | production | staging
    debug: bool = True
    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), "../../.env"), env_file_encoding='utf-8', extra='allow')

    # Supabase
    db_url: str = Field(..., alias="database_url")
    db_key: SecretStr = Field(..., alias="database_key")
    max_result_rag : int = Field(..., alias="max_result_rag")
    embedding_model : str = Field(..., alias="embedding_model")
    threshold : float = Field(..., alias="threshold")
    
    # OpenAi
    openai_key : SecretStr = Field(..., alias="OPENAI_API_KEY")
    model : str = Field(..., alias="model")
    
    # Tavily
    tavily_key : SecretStr = Field(..., alias="TAVILY_API_KEY")
    max_result_tavily : int = Field(..., alias="max_result_tavily")
    
    # Otros (opcional: CORS, JWT, etc.)
    allowed_origins: list[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]
    


SETTINGS = Settings()