from fastapi import APIRouter, Depends, Request

from controllers import depositor_controller
from utils.auth import require_user
from utils.db import get_connection

router = APIRouter()


@router.get("/api/depositors")
def list_depositors(request: Request, connection=Depends(get_connection), user=Depends(require_user)):
    return depositor_controller.list_depositors(connection, request.query_params)


@router.post("/api/depositors")
async def create_depositor(request: Request, connection=Depends(get_connection), user=Depends(require_user)):
    body = await request.json()
    return depositor_controller.create_depositor(connection, body, user)


@router.get("/api/depositors/options")
def list_options(connection=Depends(get_connection), user=Depends(require_user)):
    return depositor_controller.list_options(connection)


@router.get("/api/depositors/{depositor_id}")
def get_depositor(depositor_id: int, connection=Depends(get_connection), user=Depends(require_user)):
    return depositor_controller.get_depositor(connection, depositor_id)


@router.put("/api/depositors/{depositor_id}")
async def update_depositor(depositor_id: int, request: Request, connection=Depends(get_connection), user=Depends(require_user)):
    body = await request.json()
    return depositor_controller.update_depositor(connection, depositor_id, body)


@router.delete("/api/depositors/{depositor_id}")
def delete_depositor(depositor_id: int, connection=Depends(get_connection), user=Depends(require_user)):
    return depositor_controller.delete_depositor(connection, depositor_id)
