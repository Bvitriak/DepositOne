from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass
class Deposit:
    id: int
    depositor_id: int
    depositor_name: str
    currency_id: int
    currency: str
    status: str
    amount: Decimal
    interest_rate: Decimal
    start_date: date
    end_date: date
    created_at: datetime
    ordinal: int
