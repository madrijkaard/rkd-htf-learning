from pydantic import BaseModel

class CandleRequest(BaseModel):
    symbol: str
    interval: str

class CandleResponse(BaseModel):
    symbol: str
    interval: str
    open: float
    close: float
    high: float
    low: float
