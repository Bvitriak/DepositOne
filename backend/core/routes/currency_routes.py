from fastapi import APIRouter, Depends

from controllers import currency_controller
from utils.auth import require_user
from utils.db import get_connection

router = APIRouter()


@router.get("/api/currencies")
def list_currencies(connection=Depends(get_connection), user=Depends(require_user)):
    return currency_controller.list_currencies(connection)
