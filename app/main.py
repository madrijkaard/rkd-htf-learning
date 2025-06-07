from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routers import candlestick, order_book, learning
from app.services.heatmap import generate_heatmap_data

app = FastAPI()

# Monta a pasta 'static' para arquivos estáticos (JS, CSS, imagens, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Diretório onde estão os templates HTML
templates = Jinja2Templates(directory="app/templates")

# Rotas de módulos existentes
app.include_router(candlestick.router, prefix="/candlestick", tags=["Candlestick"])
app.include_router(order_book.router, prefix="/order-book", tags=["Order Book"])
app.include_router(learning.router, prefix="/learning", tags=["Learning"])

# Rota para renderizar o heatmap de uma cripto específica
@app.get("/heatmap")
async def render_heatmap(request: Request, symbol: str = Query(...)):
    heatmap_data = generate_heatmap_data(symbol)
    return templates.TemplateResponse("heatmap.html", {
        "request": request,
        "heatmap_data": heatmap_data,
        "symbol": symbol
    })
