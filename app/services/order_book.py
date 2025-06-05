import os
import csv
import requests
from pathlib import Path

def capture_order_book(symbol: str):
    base_url = "https://api.binance.com/api/v3/depth"
    params = {"symbol": symbol.upper(), "limit": 50}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()

    # Ex: ETHUSDT -> ETH
    symbol_prefix = symbol.replace("USDT", "")

    bids_path = Path(f"data/bids/{symbol_prefix}.csv")
    asks_path = Path(f"data/asks/{symbol_prefix}.csv")

    # Garante que diretórios existem
    bids_path.parent.mkdir(parents=True, exist_ok=True)
    asks_path.parent.mkdir(parents=True, exist_ok=True)

    # Remove arquivos antigos se existirem
    if bids_path.exists():
        bids_path.unlink()
    if asks_path.exists():
        asks_path.unlink()

    # Salva novos arquivos
    _write_order_book_csv(bids_path, data["bids"])
    _write_order_book_csv(asks_path, data["asks"])

def _write_order_book_csv(file_path: Path, entries: list):
    with open(file_path, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["price", "amount"])
        for price, amount in entries:
            writer.writerow([price, amount])
