from fastapi import APIRouter, Depends, Request

from controllers import report_controller
from utils.auth import require_user
from utils.db import get_connection

router = APIRouter()


@router.get("/api/reports")
def list_reports(request: Request, connection=Depends(get_connection), user=Depends(require_user)):
    return report_controller.list_reports(connection, request.query_params)


@router.get("/api/reports/cash-flow")
def get_cash_flow(connection=Depends(get_connection), user=Depends(require_user)):
    return report_controller.get_cash_flow(connection)
