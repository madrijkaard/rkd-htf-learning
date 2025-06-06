import asyncio
from datetime import datetime
from app.services.order_book import capture_order_book, reset_order_book_files
from app.config.settings import settings

running = False
task: asyncio.Task | None = None

async def _run_schedule():
    while running:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [schedule] Capturando order book de {settings.symbol}...")
        try:
            capture_order_book(settings.symbol)
        except Exception as e:
            print(f"[{timestamp}] [schedule] Erro: {e}")
        await asyncio.sleep(60)

async def start_schedule():
    global running, task
    if not running:
        reset_order_book_files(settings.symbol)
        running = True
        task = asyncio.create_task(_run_schedule())
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [schedule] Agendador iniciado.")

async def stop_schedule():
    global running, task
    running = False
    if task:
        task.cancel()
        task = None
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [schedule] Agendador parado.")
