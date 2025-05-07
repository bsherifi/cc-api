import os
from typing import Dict, Any, Optional

from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "Currency Converter API"
    API_V1_STR: str = "/api/v1"
    
    # External API settings
    EXCHANGE_API_KEY: str = os.environ.get("EXCHANGE_API_KEY", "3afdfcec62a73d0467a5ae1e")
    EXCHANGE_API_BASE_URL: str = os.environ.get("EXCHANGE_API_BASE_URL", "https://v6.exchangerate-api.com/v6/")
    
    # Plan defaults
    PLANS: Dict[str, Dict[str, Any]] = {
        "free": {"name": "Free", "rate_limit": 10, "initial_credits": 100},
        "pro": {"name": "Pro", "rate_limit": 60, "initial_credits": 1000},
        "diamond": {"name": "Diamond", "rate_limit": 120, "initial_credits": 5000},
    }
    
    # Credits per request
    CREDITS_PER_CONVERSION: int = 1
    CREDITS_PER_HISTORICAL: int = 1


settings = Settings() 