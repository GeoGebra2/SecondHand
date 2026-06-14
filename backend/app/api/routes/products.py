from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.product import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    ProductCreateRequest,
    ProductQueryParams,
    ProductUpdateRequest,
)
from app.services.product_service import service as product_service

router = APIRouter()


@router.get('', response_model=ApiResponse)
def list_products(
    keyword: str | None = Query(default=None, max_length=100),
    category_id: int | None = Query(default=None, gt=0),
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    sort_by: str = Query(default='publish_time', pattern='^(publish_time|price)$'),
    sort_order: str = Query(default='desc', pattern='^(asc|desc)$'),
    include_offline: bool = False,
    db: Session = Depends(get_db),
) -> ApiResponse:
    try:
        params = ProductQueryParams(
            keyword=keyword,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            sort_by=sort_by,
            sort_order=sort_order,
            include_offline=include_offline,
        )
        products = product_service.list_products(db, params)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ApiResponse(
        message='获取商品列表成功',
        data=[product.model_dump(mode='json') for product in products],
    )


@router.get('/mine', response_model=ApiResponse)
def list_my_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    products = product_service.list_my_products(db, current_user)
    return ApiResponse(
        message='获取我发布的商品成功',
        data=[product.model_dump(mode='json') for product in products],
    )


@router.get('/categories', response_model=ApiResponse)
def list_categories(
    include_disabled: bool = False,
    db: Session = Depends(get_db),
) -> ApiResponse:
    categories = product_service.list_categories(db, include_disabled)
    return ApiResponse(
        message='获取分类列表成功',
        data=[category.model_dump(mode='json') for category in categories],
    )


@router.post('/categories', response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        category = product_service.create_category(db, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ApiResponse(
        message='分类创建成功',
        data=category.model_dump(mode='json'),
    )


@router.put('/categories/{category_id}', response_model=ApiResponse)
def update_category(
    category_id: int,
    payload: CategoryUpdateRequest,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        category = product_service.update_category(db, category_id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ApiResponse(
        message='分类更新成功',
        data=category.model_dump(mode='json'),
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


@router.put('/{product_id}', response_model=ApiResponse)
def update_product(
    product_id: int,
    payload: ProductUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        product = product_service.update_product(db, product_id, current_user, payload)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ApiResponse(
        message='商品更新成功',
        data=product.model_dump(mode='json'),
    )


@router.patch('/{product_id}/offline', response_model=ApiResponse)
def offline_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        product = product_service.offline_product(db, product_id, current_user)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ApiResponse(
        message='商品下架成功',
        data=product.model_dump(mode='json'),
    )


@router.patch('/{product_id}/relist', response_model=ApiResponse)
def relist_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        product = product_service.relist_product(db, product_id, current_user)
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ApiResponse(
        message='商品重新上架成功',
        data=product.model_dump(mode='json'),
    )
