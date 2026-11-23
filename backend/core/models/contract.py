from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass
class Contract:
    id: int
    ordinal: int
    deposit_id: int
    deposit_ordinal: int
    depositor_id: int
    depositor_name: str
    currency: str
    amount: Decimal
    interest_rate: Decimal
    start_date: date
    end_date: date
    contract_date: date
    signing_status: str
    description: str
    special_conditions: str
    created_at: datetime
