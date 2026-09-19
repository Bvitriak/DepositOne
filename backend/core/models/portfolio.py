from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Portfolio:
    depositors: int
    active_deposits: int
    total_amount: Decimal
    signed_contracts: int
    pending_contracts: int
    rejected_contracts: int
