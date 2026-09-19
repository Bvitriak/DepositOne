from fastapi import APIRouter, Depends, Request

from controllers import portfolio_controller
from utils.auth import require_user
from utils.db import get_connection

router = APIRouter()


@router.get("/api/portfolio")
def get_portfolio(request: Request, connection=Depends(get_connection), user=Depends(require_user)):
    return portfolio_controller.get_portfolio(connection, request.query_params)
