from fastapi import APIRouter, Depends, Request

from controllers import deposit_controller
from utils.auth import require_user
from utils.db import get_connection

router = APIRouter()


@router.get("/api/deposits")
def list_deposits(request: Request, connection=Depends(get_connection), user=Depends(require_user)):
    return deposit_controller.list_deposits(connection, request.query_params)


@router.post("/api/deposits")
async def create_deposit(request: Request, connection=Depends(get_connection), user=Depends(require_user)):
    body = await request.json()
    return deposit_controller.create_deposit(connection, body, user)


@router.get("/api/deposits/options")
def list_options(connection=Depends(get_connection), user=Depends(require_user)):
    return deposit_controller.list_options(connection)


@router.get("/api/deposits/stats")
def get_stats(connection=Depends(get_connection), user=Depends(require_user)):
    return deposit_controller.get_stats(connection)


@router.get("/api/deposits/{deposit_id}")
def get_deposit(deposit_id: int, connection=Depends(get_connection), user=Depends(require_user)):
    return deposit_controller.get_deposit(connection, deposit_id)


@router.put("/api/deposits/{deposit_id}")
async def update_deposit(deposit_id: int, request: Request, connection=Depends(get_connection), user=Depends(require_user)):
    body = await request.json()
    return deposit_controller.update_deposit(connection, deposit_id, body)


@router.delete("/api/deposits/{deposit_id}")
def delete_deposit(deposit_id: int, connection=Depends(get_connection), user=Depends(require_user)):
    return deposit_controller.delete_deposit(connection, deposit_id)
