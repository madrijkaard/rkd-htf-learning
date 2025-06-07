import asyncio
from datetime import datetime
from app.services.order_book import capture_order_book, reset_order_book_files
from app.config.settings import settings

# Mapeia símbolo → task assíncrona
tasks: dict[str, asyncio.Task] = {}
running = False

async def _run_schedule(symbol: str):
    """
    Executa captura contínua de order book para um símbolo específico.
    """
    while running:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [schedule] Capturando order book de {symbol}...")
        try:
            capture_order_book(symbol)
        except Exception as e:
            print(f"[{timestamp}] [schedule] Erro ao capturar {symbol}: {e}")
        await asyncio.sleep(settings.capture_interval_seconds)

async def start_schedule():
    """
    Inicia os agendadores para todos os símbolos configurados.
    """
    global running, tasks
    if not running:
        running = True
        print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [schedule] Iniciando agendadores...")
        for symbol in settings.symbols:
            try:
                reset_order_book_files(symbol)
                task = asyncio.create_task(_run_schedule(symbol))
                tasks[symbol] = task
                print(f"  ✔ Agendador para {symbol} iniciado.")
            except Exception as e:
                print(f"  ✖ Erro ao iniciar agendador para {symbol}: {e}")

async def stop_schedule():
    """
    Interrompe todos os agendadores em execução.
    """
    global running, tasks
    running = False
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] [schedule] Parando todos os agendadores...")
    for symbol, task in tasks.items():
        task.cancel()
        print(f"  ✖ Agendador para {symbol} cancelado.")
    tasks.clear()
