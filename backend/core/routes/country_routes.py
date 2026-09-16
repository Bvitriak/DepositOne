from fastapi import APIRouter, Depends

from controllers import country_controller
from utils.auth import require_user
from utils.db import get_connection

router = APIRouter()


@router.get("/api/countries")
def list_countries(connection=Depends(get_connection), user=Depends(require_user)):
    return country_controller.list_countries(connection)
