import csv
import time
import requests
from pathlib import Path

def capture_order_book(symbol: str):
    """
    Captura os dados atuais do order book (bids e asks) da Binance
    e adiciona nos arquivos .csv correspondentes, incluindo timestamp.
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

    _append_order_book_csv(bids_path, data["bids"])
    _append_order_book_csv(asks_path, data["asks"])

def reset_order_book_files(symbol: str):
    """
    Limpa os arquivos .csv e escreve apenas o cabeçalho (uma única vez)
    no início da execução do serviço.
    """
    symbol_prefix = symbol.replace("USDT", "")
    bids_path = Path(f"data/bids/{symbol_prefix}.csv")
    asks_path = Path(f"data/asks/{symbol_prefix}.csv")

    bids_path.parent.mkdir(parents=True, exist_ok=True)
    asks_path.parent.mkdir(parents=True, exist_ok=True)

    with open(bids_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "price", "volume"])  # <- corrigido

    with open(asks_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "price", "volume"])  # <- corrigido

def _append_order_book_csv(file_path: Path, entries: list):
    """
    Acrescenta linhas no arquivo CSV com os dados capturados, incluindo timestamp.
    """
    timestamp = int(time.time())  # tempo atual (epoch)
    
    with open(file_path, mode="a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        for price, volume in entries:  # <- ajustado para refletir a nova coluna
            writer.writerow([timestamp, price, volume])
