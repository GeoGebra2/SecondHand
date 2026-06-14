from fastapi import APIRouter

from app.api.routes import admin, auth, health, orders, products, reports, reviews

api_router = APIRouter()
api_router.include_router(health.router, prefix='/health', tags=['health'])
api_router.include_router(auth.router, prefix='/auth', tags=['auth'])
api_router.include_router(products.router, prefix='/products', tags=['products'])
api_router.include_router(orders.router, prefix='/orders', tags=['orders'])
api_router.include_router(reviews.router, prefix='/reviews', tags=['reviews'])
api_router.include_router(reports.router, prefix='/reports', tags=['reports'])
api_router.include_router(admin.router, prefix='/admin', tags=['admin'])
