from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.product import ProductCreateRequest
from app.services.product_service import service as product_service

router = APIRouter()


@router.get('', response_model=ApiResponse)
def list_products(db: Session = Depends(get_db)) -> ApiResponse:
    products = product_service.list_products(db)
    return ApiResponse(
        message='获取商品列表成功',
        data=[product.model_dump(mode='json') for product in products],
    )


@router.post('', response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        product = product_service.create_product(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ApiResponse(
        message='商品发布成功',
        data=product.model_dump(mode='json'),
    )
