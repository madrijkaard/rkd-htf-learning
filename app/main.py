from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import candlestick, order_book, learning

app = FastAPI()

# Monta a pasta 'static' para arquivos estáticos (JS, CSS, imagens, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Diretório onde estão os templates HTML (usado internamente pelos routers)
templates = Jinja2Templates(directory="app/templates")

# Registra os módulos de rotas
app.include_router(candlestick.router, prefix="/candlesticks", tags=["Candlestick"])
app.include_router(order_book.router, prefix="/order-books", tags=["Order Book"])
app.include_router(learning.router, prefix="/learnings", tags=["Learning"])
