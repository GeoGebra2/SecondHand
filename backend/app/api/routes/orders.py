from fastapi import APIRouter

from app.schemas.common import ApiResponse

router = APIRouter()


@router.get('', response_model=ApiResponse)
def list_orders() -> ApiResponse:
    return ApiResponse(
        message='order list placeholder',
        data=[
            {'id': 'ORD-001', 'product': '考研英语资料', 'status': 'PENDING'},
            {'id': 'ORD-002', 'product': '平板支架', 'status': 'IN_PROGRESS'},
        ],
    )


@router.patch('/{order_id}/finish', response_model=ApiResponse)
def finish_order(order_id: str) -> ApiResponse:
    return ApiResponse(message='finish order placeholder', data={'order_id': order_id, 'status': 'DONE'})
