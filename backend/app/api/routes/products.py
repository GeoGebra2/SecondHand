from fastapi import APIRouter

from app.schemas.common import ApiResponse

router = APIRouter()


@router.get('', response_model=ApiResponse)
def list_products() -> ApiResponse:
    return ApiResponse(
        message='product list placeholder',
        data=[
            {'id': 1, 'title': '高数教材', 'category': '教材资料', 'price': 25, 'status': 'ON_SALE'},
            {'id': 2, 'title': '机械键盘', 'category': '数码产品', 'price': 120, 'status': 'RESERVED'},
        ],
    )


@router.post('', response_model=ApiResponse)
def create_product() -> ApiResponse:
    return ApiResponse(message='create product placeholder', data={'created': True})
