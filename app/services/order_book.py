import csv
import time
import requests
from pathlib import Path

def get_current_price(symbol: str) -> float:
    """
    Consulta o preço atual de mercado da criptomoeda via API da Binance.
    """
    url = "https://api.binance.com/api/v3/ticker/price"
    response = requests.get(url, params={"symbol": symbol.upper()})
    response.raise_for_status()
    return float(response.json()["price"])

def capture_order_book(symbol: str):
    """
    Captura os dados atuais do order book (bids e asks) da Binance
    e adiciona nos arquivos .csv correspondentes, incluindo timestamp
    e o preço de mercado no momento.
    """
    base_url = "https://api.binance.com/api/v3/depth"
    params = {"symbol": symbol.upper(), "limit": 100}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    symbol_prefix = symbol.replace("USDT", "")
    bids_path = Path(f"data/bids/{symbol_prefix}.csv")
    asks_path = Path(f"data/asks/{symbol_prefix}.csv")

    bids_path.parent.mkdir(parents=True, exist_ok=True)
    asks_path.parent.mkdir(parents=True, exist_ok=True)

    _append_order_book_csv(bids_path, data["bids"], symbol)
    _append_order_book_csv(asks_path, data["asks"], symbol)

def reset_order_book_files(symbol: str):
    """
    Limpa os arquivos .csv e escreve apenas o cabeçalho no início da execução.
    """
    symbol_prefix = symbol.replace("USDT", "")
    bids_path = Path(f"data/bids/{symbol_prefix}.csv")
    asks_path = Path(f"data/asks/{symbol_prefix}.csv")

    bids_path.parent.mkdir(parents=True, exist_ok=True)
    asks_path.parent.mkdir(parents=True, exist_ok=True)

    with open(bids_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "price", "volume", "current_price"])

    with open(asks_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "price", "volume", "current_price"])

def _append_order_book_csv(file_path: Path, entries: list, symbol: str):
    """
    Acrescenta linhas no CSV com os dados capturados, incluindo timestamp e preço atual.
    """
    timestamp = int(time.time())
    current_price = get_current_price(symbol)

    with open(file_path, mode="a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        for price, volume in entries:
            writer.writerow([timestamp, price, volume, current_price])
