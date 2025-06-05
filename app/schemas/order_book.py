from pydantic import BaseModel

class OrderBookRequest(BaseModel):
    symbol: str
