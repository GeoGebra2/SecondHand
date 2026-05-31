from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.order import OrderActionRequest, OrderCreateRequest
from app.services.order_service import service as order_service

router = APIRouter()


@router.get('', response_model=ApiResponse)
def list_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    orders = order_service.list_orders(db, current_user)
    return ApiResponse(
        message='获取订单列表成功',
        data=[order.model_dump(mode='json') for order in orders],
    )


@router.post('', response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        order = order_service.create_order(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return ApiResponse(
        message='创建订单成功',
        data=order.model_dump(mode='json'),
    )


@router.patch('/{order_id}/confirm', response_model=ApiResponse)
def confirm_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        result = order_service.confirm_order(db, order_id, current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ApiResponse(message='订单确认成功', data=result.model_dump(mode='json'))


@router.patch('/{order_id}/complete', response_model=ApiResponse)
def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        result = order_service.complete_order(db, order_id, current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ApiResponse(message='订单完成成功', data=result.model_dump(mode='json'))


@router.patch('/{order_id}/cancel', response_model=ApiResponse)
def cancel_order(
    order_id: int,
    payload: OrderActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    try:
        result = order_service.cancel_order(db, order_id, current_user, payload.cancel_reason)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return ApiResponse(message='订单取消成功', data=result.model_dump(mode='json'))
