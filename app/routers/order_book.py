from fastapi import APIRouter, status, Request, Query
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from app.schedules import order_book as order_book_schedule
from app.services.heatmap import generate_heatmap_data

router = APIRouter()

# Inicializa os templates
templates = Jinja2Templates(directory="app/templates")

@router.post("/capture/start", status_code=status.HTTP_202_ACCEPTED)
async def start_schedule():
    """
    Inicia os agendadores para todos os símbolos definidos no .env.
    Retorna mensagem diferente se o agendador já estiver em execução.
    """
    started = await order_book_schedule.start_schedule()
    if not started:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Agendador já está em execução."}
        )
    return {"message": "Agendador iniciado."}

@router.post("/capture/stop", status_code=status.HTTP_202_ACCEPTED)
async def stop_schedule():
    """
    Para todos os agendadores de captura de order book.
    """
    await order_book_schedule.stop_schedule()
    return {"message": "Agendador parado."}

@router.get("/capture/status", status_code=status.HTTP_200_OK)
def get_schedule_status():
    """
    Retorna se o agendador está ativo ou não.
    """
    status_str = "ativo" if order_book_schedule.is_running() else "inativo"
    return {"status": status_str}

@router.get("/heatmap")
async def render_heatmap(
    request: Request,
    symbol: str = Query(..., description="Símbolo da cripto (ex: BTCUSDT)"),
    bucket_price: float = Query(None, description="Intervalo de preços no eixo Y (ex: 100.0)"),
    bucket_time: str = Query("5min", description="Intervalo de tempo no eixo X (ex: 10min, 30min, 1h)")
):
    """
    Renderiza o heatmap para o símbolo especificado, com controle de buckets de preço e tempo.
    """
    heatmap_data = generate_heatmap_data(symbol, bucket_price, bucket_time)
    return templates.TemplateResponse("heatmap.html", {
        "request": request,
        "heatmap_data": heatmap_data,
        "symbol": symbol,
        "bucket_price": bucket_price,
        "bucket_time": bucket_time
    })
