from fastapi import APIRouter, Depends, Request

from controllers import plan_controller
from utils.auth import require_user
from utils.db import get_connection

router = APIRouter()


@router.get("/api/plans")
def list_plans(request: Request, connection=Depends(get_connection), user=Depends(require_user)):
    return plan_controller.list_plans(connection, request.query_params)


@router.get("/api/plans/summary")
def get_summary(connection=Depends(get_connection), user=Depends(require_user)):
    return plan_controller.get_summary(connection)


@router.get("/api/plans/{deposit_id}")
def get_plan(deposit_id: int, connection=Depends(get_connection), user=Depends(require_user)):
    return plan_controller.get_plan(connection, deposit_id)
