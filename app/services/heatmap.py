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

        # Converte timestamp para horário local
        df["timestamp"] = (
            pd.to_datetime(df["timestamp"], unit='s')
            .dt.tz_localize("UTC")
            .dt.tz_convert("America/Sao_Paulo")
        )

        df["price"] = pd.to_numeric(df["price"])
        df["volume"] = pd.to_numeric(df["volume"])

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

def _create_heatmap(df: pd.DataFrame, title: str, avg_price: float):
    try:
        if df.empty:
            return "<p style='color:red;'>Dados vazios</p>"

        pivot = df.groupby(["price_bucket", "time_bucket"])["volume"].sum().unstack(fill_value=0)
        pivot = pivot.sort_index(ascending=True)

        z_data = pivot.values
        z_data = (z_data - np.min(z_data)) / (np.max(z_data) - np.min(z_data) + 0.001)
        z_data = np.nan_to_num(z_data, nan=0, posinf=1, neginf=0)

        fig = go.Figure(go.Heatmap(
            z=z_data,
            x=pivot.columns.strftime("%d, %H:%M"),
            y=[f"{p:.4f}" for p in pivot.index],
            colorscale='Viridis',
            zmin=0,
            zmax=1,
            colorbar=dict(title="Liquidez Normalizada")
        ))

        fig.update_layout(
            xaxis_title="Tempo (Horário Local)",
            yaxis_title="Faixa de Preço",
            height=400,
            margin=dict(t=20, b=40, l=50, r=50),
            title=None
        )

        return pio.to_html(fig, full_html=False)

    except Exception as e:
        return f"<p style='color:red;'>Erro ao gerar heatmap: {str(e)}</p>"

def generate_heatmap_data(symbol: str, bucket_price: float = None, bucket_time: str = "5min"):
    bids_path = Path(f"data/bids/{symbol}.csv")
    asks_path = Path(f"data/asks/{symbol}.csv")

    bids_df, bids_err, bids_avg = _load_and_prepare_data(bids_path, bucket_price, bucket_time)
    asks_df, asks_err, asks_avg = _load_and_prepare_data(asks_path, bucket_price, bucket_time)

    bids_html = _create_heatmap(bids_df, "Bids", bids_avg) if bids_df is not None else bids_err
    asks_html = _create_heatmap(asks_df, "Asks", asks_avg) if asks_df is not None else asks_err

    return (
        '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'
        '<div style="display: flex; flex-direction: column; gap: 20px; padding: 20px;">'
        f'<div>{asks_html}</div>'
        f'<div>{bids_html}</div>'
        '</div>'
    )
