import asyncio
from app.services.order_book import capture_order_book
from app.config.settings import settings

running = False
task: asyncio.Task | None = None

async def _run_schedule():
    while running:
        print(f"[schedule] Capturando order book de {settings.symbol}...")
        try:
            capture_order_book(settings.symbol)
        except Exception as e:
            print(f"[schedule] Erro: {e}")
        await asyncio.sleep(60)

async def start_schedule():
    global running, task
    if not running:
        running = True
        task = asyncio.create_task(_run_schedule())  # ✅ agora dentro de função async
        print("[schedule] Agendador iniciado.")

async def stop_schedule():
    global running, task
    running = False
    if task:
        task.cancel()
        task = None
        print("[schedule] Agendador parado.")
