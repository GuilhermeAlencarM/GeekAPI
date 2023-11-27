from fastapi import APIRouter

from api.v1.endpoints import carrinho

api_router = APIRouter()
api_router.include_router(carrinho.router)
