from fastapi import APIRouter
from app.schemas.candlestick import CandleRequest, CandleResponse

router = APIRouter()

@router.post("/", response_model=CandleResponse)
def get_candlestick(data: CandleRequest):
    # lógica mockada
    return CandleResponse(
        symbol=data.symbol,
        interval=data.interval,
        open=100.0,
        close=105.0,
        high=110.0,
        low=95.0
    )
