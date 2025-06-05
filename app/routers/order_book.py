from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.schemas.order_book import OrderBookRequest
from app.services.order_book import capture_order_book
from app.schedules import order_book as order_book_schedule

router = APIRouter()

@router.post("/capture", status_code=status.HTTP_201_CREATED)
def capture(data: OrderBookRequest):
    capture_order_book(data.symbol)
    return JSONResponse(status_code=201, content={"message": "Captura manual realizada."})

@router.post("/capture/start")
async def start_schedule():
    await order_book_schedule.start_schedule()
    return {"message": "Agendador iniciado."}

@router.post("/capture/stop")
async def stop_schedule():
    await order_book_schedule.stop_schedule()
    return {"message": "Agendador parado."}
