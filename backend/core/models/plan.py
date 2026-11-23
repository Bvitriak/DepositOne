from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class Plan:
    deposit_id: int
    ordinal: int
    contract_ordinal: int
    depositor_id: int
    depositor_name: str
    phone: str
    email: str
    currency: str
    amount: Decimal
    interest_rate: Decimal
    start_date: date
    end_date: date
