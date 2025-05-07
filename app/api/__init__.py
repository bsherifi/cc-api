from fastapi import APIRouter

from app.api.endpoints import auth, currency

api_router = APIRouter()

# Include the auth router
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include the currency router
api_router.include_router(currency.router, prefix="/currency", tags=["currency"])
