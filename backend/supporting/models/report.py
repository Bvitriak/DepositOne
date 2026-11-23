from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Report:
    depositor_id: int
    depositor_name: str
    deposits: int
    total_amount: Decimal
    total_income: Decimal
