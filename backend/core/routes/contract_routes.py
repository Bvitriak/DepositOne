from fastapi import APIRouter, Depends, Request

from controllers import contract_controller
from utils.auth import require_user
from utils.db import get_connection

router = APIRouter()


@router.get("/api/contracts")
def list_contracts(request: Request, connection=Depends(get_connection), user=Depends(require_user)):
    return contract_controller.list_contracts(connection, request.query_params)


@router.post("/api/contracts")
async def create_contract(request: Request, connection=Depends(get_connection), user=Depends(require_user)):
    body = await request.json()
    return contract_controller.create_contract(connection, body, user)


@router.get("/api/contracts/{contract_id}")
def get_contract(contract_id: int, connection=Depends(get_connection), user=Depends(require_user)):
    return contract_controller.get_contract(connection, contract_id)


@router.put("/api/contracts/{contract_id}")
async def update_contract(contract_id: int, request: Request, connection=Depends(get_connection), user=Depends(require_user)):
    body = await request.json()
    return contract_controller.update_contract(connection, contract_id, body)


@router.delete("/api/contracts/{contract_id}")
def delete_contract(contract_id: int, connection=Depends(get_connection), user=Depends(require_user)):
    return contract_controller.delete_contract(connection, contract_id)
