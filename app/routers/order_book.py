from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.schedules import order_book as order_book_schedule

router = APIRouter()

@router.post("/capture/start", status_code=status.HTTP_202_ACCEPTED)
async def start_schedule():
    """
    Inicia os agendadores para todos os símbolos definidos no .env.
    """
    await order_book_schedule.start_schedule()
    return {"message": "Agendador iniciado."}

@router.post("/capture/stop", status_code=status.HTTP_202_ACCEPTED)
async def stop_schedule():
    """
    Para todos os agendadores de captura de order book.
    """
    await order_book_schedule.stop_schedule()
    return {"message": "Agendador parado."}
