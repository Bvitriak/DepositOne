from dataclasses import dataclass
from datetime import date, datetime


@dataclass
class Depositor:
    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    country_id: int
    country: str
    passport: str
    tin: str
    phone: str
    email: str
    address: str
    created_at: datetime
