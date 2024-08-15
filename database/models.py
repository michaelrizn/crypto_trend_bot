from dataclasses import dataclass

@dataclass
class Signal:
    id: int
    name: str
    trend: str
    date_start: str
    date_last: str
    accuracy: float
    date_end: str
    price_start: float
    price_last: float
    price_end: float
    count_sends: int
    reported: int