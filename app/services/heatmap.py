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
    """
    Define bucket_size com base na variação de preços observada.
    Garante cerca de 30 buckets no eixo Y.
    """
    faixa = preco_max - preco_min
    bucket = faixa / 30 if faixa > 0 else 0.001
    return round(bucket, 6)

def _load_and_prepare_data(file_path: Path):
    """Carrega e prepara um único arquivo CSV"""
    try:
        if not file_path.exists():
            return None, f"Arquivo não encontrado: {file_path}", None
        
        df = pd.read_csv(file_path)
        if not {"timestamp", "price", "volume"}.issubset(df.columns):
            return None, "Arquivo CSV inválido", None

        # Converter tipos
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit='s')
        df["price"] = pd.to_numeric(df["price"])
        df["volume"] = pd.to_numeric(df["volume"])

        preco_min = df["price"].min()
        preco_max = df["price"].max()
        bucket_size = definir_bucket_size(preco_min, preco_max)
        avg_price = df["price"].mean()

        # Agrupamento por faixa de preço
        df["price_bucket"] = (df["price"] // bucket_size) * bucket_size

        # Agrupamento por tempo de 5 minutos
        df["time_bucket"] = df["timestamp"].dt.floor("5min")

        return df, None, avg_price

    except Exception as e:
        logger.error(f"Erro ao carregar dados de {file_path}: {str(e)}")
        return None, f"Erro: {str(e)}", None

def _create_heatmap(df: pd.DataFrame, title: str, avg_price: float):
    """Cria heatmap com a evolução da liquidez ao longo do tempo"""
    try:
        if df.empty:
            return "<p style='color:red;'>Dados vazios</p>"

        pivot = df.groupby(["price_bucket", "time_bucket"])["volume"].sum().unstack(fill_value=0)
        pivot = pivot.sort_index(ascending=False)

        z_data = pivot.values
        z_data = (z_data - np.min(z_data)) / (np.max(z_data) - np.min(z_data) + 0.001)
        z_data = np.nan_to_num(z_data, nan=0, posinf=1, neginf=0)

        fig = go.Figure(go.Heatmap(
            z=z_data,
            x=pivot.columns.strftime("%d, %H:%M"),
            y=[f"{p:.4f}" if p < 1 else f"{p:.4f}" for p in pivot.index],
            colorscale='Viridis',
            zmin=0,
            zmax=1,
            colorbar=dict(title="Liquidez Normalizada")
        ))

        fig.update_layout(
            title=f"{title} (Preço Médio: {avg_price:.2f})",
            xaxis_title="Tempo",
            yaxis_title="Faixa de Preço",
            height=700
        )

        return pio.to_html(fig, full_html=False)

    except Exception as e:
        return f"<p style='color:red;'>Erro ao gerar heatmap: {str(e)}</p>"

def generate_heatmap_data(symbol: str):
    """Gera heatmaps para uma cripto específica"""
    bids_path = Path(f"data/bids/{symbol}.csv")
    asks_path = Path(f"data/asks/{symbol}.csv")

    bids_df, bids_err, bids_avg = _load_and_prepare_data(bids_path)
    asks_df, asks_err, asks_avg = _load_and_prepare_data(asks_path)

    bids_html = _create_heatmap(bids_df, "Bids", bids_avg) if bids_df is not None else bids_err
    asks_html = _create_heatmap(asks_df, "Asks", asks_avg) if asks_df is not None else asks_err

    return (
        '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'
        '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px;">'
        f'<div>{bids_html}</div>'
        f'<div>{asks_html}</div>'
        '</div>'
    )
