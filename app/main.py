from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routers import candlestick, order_book, learning
from app.services.heatmap import generate_heatmap_data

app = FastAPI()

# Monta pasta static (caso queira usar JS/CSS personalizados)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define onde estão os templates HTML
templates = Jinja2Templates(directory="app/templates")

# Rotas já existentes
app.include_router(candlestick.router, prefix="/candlestick", tags=["Candlestick"])
app.include_router(order_book.router, prefix="/order-book", tags=["Order Book"])
app.include_router(learning.router, prefix="/learning", tags=["Learning"])

# Nova rota para visualização do heatmap
@app.get("/heatmap")
async def render_heatmap(request: Request):
    heatmap_data = generate_heatmap_data()
    return templates.TemplateResponse("heatmap.html", {
        "request": request,
        "heatmap_data": heatmap_data
    })
