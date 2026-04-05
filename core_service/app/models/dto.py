from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class DepositorData:
    created_by_user_id: int
    last_name: str
    first_name: str
    middle_name: str | None
    passport_series: str
    passport_number: str
    issued_by: str | None
    phone: str | None
    email: str | None
    address: str | None

@dataclass(slots=True)
class DepositData:
    depositor_id: int
    opened_by_user_id: int
    deposit_type: str
    amount: float
    interest_rate: float
    start_date: str
    end_date: str
    currency: str
    capitalization: int
    auto_renewal: int
    status: str
