import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import logging
from pathlib import Path
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def definir_bucket_size(preco_min: float, preco_max: float) -> float:
    faixa = preco_max - preco_min
    bucket = faixa / 30 if faixa > 0 else 0.001
    return round(bucket, 6)


def _load_and_prepare_data(file_path: Path, bucket_price: float = None, bucket_time: str = "5min"):
    try:
        if not file_path.exists():
            return None, f"Arquivo não encontrado: {file_path}", None

        df = pd.read_csv(file_path)
        if not {"timestamp", "price", "volume"}.issubset(df.columns):
            return None, "Arquivo CSV inválido", None

        df["timestamp"] = (
            pd.to_datetime(df["timestamp"], unit='s')
            .dt.tz_localize("UTC")
            .dt.tz_convert("America/Sao_Paulo")
        )

        df["price"] = pd.to_numeric(df["price"])
        df["volume"] = pd.to_numeric(df["volume"])
        df["current_price"] = pd.to_numeric(df.get("current_price", np.nan))

        preco_min = df["price"].min()
        preco_max = df["price"].max()
        bucket_size = bucket_price if bucket_price else definir_bucket_size(preco_min, preco_max)
        avg_price = df["price"].mean()

        df["price_bucket"] = (df["price"] // bucket_size) * bucket_size
        df["time_bucket"] = df["timestamp"].dt.floor(bucket_time)

        return df, None, avg_price

    except Exception as e:
        logger.error(f"Erro ao carregar dados de {file_path}: {str(e)}")
        return None, f"Erro: {str(e)}", None


def _create_combined_heatmap(bids_df: pd.DataFrame, asks_df: pd.DataFrame, avg_price: float, side: str = None):
    try:
        if (bids_df is None or bids_df.empty) and (asks_df is None or asks_df.empty):
            return "<p style='color:red;'>Dados insuficientes</p>"

        # Filtra conforme o lado
        if side == "bid":
            combined_df = bids_df.assign(tipo="BID")
        elif side == "ask":
            combined_df = asks_df.assign(tipo="ASK")
        else:
            combined_df = pd.concat([bids_df.assign(tipo="BID"), asks_df.assign(tipo="ASK")])

        # Prepara malha de grid
        price_buckets = np.sort(combined_df["price_bucket"].unique())
        time_buckets = np.sort(combined_df["time_bucket"].unique())
        index_grid = pd.MultiIndex.from_product([price_buckets, time_buckets], names=["price_bucket", "time_bucket"])

        grouped = (
            combined_df.groupby(["price_bucket", "time_bucket"])["volume"]
            .sum()
            .reindex(index_grid, fill_value=0)
            .sort_index()
        )

        z = grouped.values
        z_normalized = (z - np.min(z)) / (np.max(z) - np.min(z) + 0.001)
        z_normalized = np.nan_to_num(z_normalized, nan=0, posinf=1, neginf=0)

        pivot = grouped.reset_index()
        time_labels = pivot["time_bucket"].dt.strftime("%d, %H:%M").unique()
        price_labels = [f"{p:.2f}" for p in sorted(price_buckets)]

        # Linha de preço de mercado (usando média de current_price)
        market_prices = combined_df
        market_line = market_prices.groupby(market_prices["timestamp"].dt.floor("5min"))["current_price"].mean()
        market_line = market_line.reindex(time_buckets, method="nearest").fillna(method="ffill")

        line_y = []
        for price in market_line:
            closest_bucket = price_buckets[np.abs(price_buckets - price).argmin()]
            line_y.append(f"{closest_bucket:.2f}")

        # Escolher cores conforme o lado
        if side == "ask":
            colorscale = [
                [0.0, "#520D6B"],
                [0.2, "#3111A4"],
                [0.4, "#1717d8"],
                [0.6, "#0d49ff"],
                [0.8, "#d7f209"],
                [1.0, "#d4ca0c"]
            ]
        elif side == "bid":
            colorscale = [
                [0.0, "#520D6B"],
                [0.2, "#3111A4"],
                [0.4, "#1717d8"],
                [0.6, "#0d49ff"],
                [0.8, "#d7f209"],
                [1.0, "#d4ca0c"]
            ]
        else:
            colorscale = [
                [0.0, "#520D6B"],
                [0.2, "#3111A4"],
                [0.4, "#1717d8"],
                [0.6, "#0d49ff"],
                [0.8, "#d7f209"],
                [1.0, "#d4ca0c"]
            ]

        fig = go.Figure()

        fig.add_trace(go.Heatmap(
            z=z_normalized.reshape(len(price_buckets), len(time_buckets)),
            x=time_labels,
            y=price_labels,
            colorscale=colorscale,
            zmin=0,
            zmax=1,
            colorbar=dict(title="Volume Normalizado")
        ))

        fig.add_trace(go.Scatter(
            x=time_labels,
            y=line_y,
            mode="lines+markers",
            name="Preço de Mercado",
            line=dict(color="white", width=2),
            marker=dict(size=4, color="white")
        ))

        titulo = f"Heatmap de Liquidez – {side.upper()}" if side in ("ask", "bid") else "Heatmap de Liquidez – ASK + BID"

        fig.update_layout(
            title=dict(text=titulo, x=0.5),
            xaxis_title="Tempo (Horário Local)",
            yaxis_title="Faixa de Preço",
            height=500,
            margin=dict(t=40, b=50, l=40, r=60),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="black")
        )

        return pio.to_html(fig, full_html=False)

    except Exception as e:
        return f"<p style='color:red;'>Erro ao gerar heatmap: {str(e)}</p>"


def generate_heatmap_data(symbol: str, bucket_price: float = None, bucket_time: str = "5min", side: str = None):
    bids_path = Path(f"data/bids/{symbol}.csv")
    asks_path = Path(f"data/asks/{symbol}.csv")

    bids_df, bids_err, bids_avg = _load_and_prepare_data(bids_path, bucket_price, bucket_time)
    asks_df, asks_err, asks_avg = _load_and_prepare_data(asks_path, bucket_price, bucket_time)

    if isinstance(bids_err, str) and side in (None, "bid"):
        return f"<p style='color:red;'>Erro em bids: {bids_err}</p>"
    if isinstance(asks_err, str) and side in (None, "ask"):
        return f"<p style='color:red;'>Erro em asks: {asks_err}</p>"

    avg_price = (bids_avg or 0) + (asks_avg or 0)
    if side == "bid":
        avg_price = bids_avg
    elif side == "ask":
        avg_price = asks_avg
    else:
        avg_price = (bids_avg + asks_avg) / 2

    return (
        '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'
        '<div style="display: flex; flex-direction: column; gap: 20px; padding: 20px;">'
        f'{_create_combined_heatmap(bids_df, asks_df, avg_price, side)}'
        '</div>'
    )
