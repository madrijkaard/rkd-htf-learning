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

def _load_and_prepare_data(folder: str):
    """Carrega e prepara todos os arquivos de uma pasta"""
    try:
        folder_path = Path(folder)
        csv_files = sorted(folder_path.glob("*.csv"))
        
        if not csv_files:
            return None, "Nenhum arquivo CSV encontrado", None
        
        # Concatena todos os arquivos da pasta
        df_list = []
        for file in csv_files:
            partial = pd.read_csv(file)
            if {"timestamp", "price", "volume"}.issubset(partial.columns):
                df_list.append(partial[["timestamp", "price", "volume"]])
        df = pd.concat(df_list, ignore_index=True)

        # Converter tipos
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit='s')
        df["price"] = pd.to_numeric(df["price"])
        df["volume"] = pd.to_numeric(df["volume"])
        
        # Agrupamento por faixa de preço de 100 unidades
        bucket_size = 100
        df["price_bucket"] = (df["price"] // bucket_size) * bucket_size
        
        # Agrupamento por tempo de 5 minutos
        df["time_bucket"] = df["timestamp"].dt.floor("5min")
        
        avg_price = df["price"].mean()
        return df, None, avg_price
        
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        return None, f"Erro: {str(e)}", None

def _create_heatmap(df: pd.DataFrame, title: str, avg_price: float):
    """Cria heatmap com a evolução da liquidez ao longo do tempo"""
    try:
        if df.empty:
            return "<p style='color:red;'>Dados vazios</p>"
            
        # Agrupar volume por faixa de preço e tempo
        pivot = df.groupby(["price_bucket", "time_bucket"])["volume"].sum().unstack(fill_value=0)
        pivot = pivot.sort_index(ascending=False)
        
        # Normalizar por coluna (opcional: para destacar onde há mais liquidez)
        z_data = pivot.values
        z_data = (z_data - np.min(z_data)) / (np.max(z_data) - np.min(z_data) + 0.001)
        z_data = np.nan_to_num(z_data, nan=0, posinf=1, neginf=0)
        
        # Criar heatmap
        fig = go.Figure(go.Heatmap(
            z=z_data,
            x=pivot.columns.strftime("%d, %H:%M"),
            y=[f"{p:.0f}" for p in pivot.index],
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
        return f"<p style='color:red;'>Erro: {str(e)}</p>"

def generate_heatmap_data():
    """Gera heatmaps com histórico de liquidez"""
    bids_df, bids_err, bids_avg = _load_and_prepare_data("data/bids")
    asks_df, asks_err, asks_avg = _load_and_prepare_data("data/asks")
    
    bids_html = _create_heatmap(bids_df, "Bids", bids_avg) if bids_df is not None else bids_err
    asks_html = _create_heatmap(asks_df, "Asks", asks_avg) if asks_df is not None else asks_err
    
    return (
        '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'
        '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px;">'
        f'<div>{bids_html}</div>'
        f'<div>{asks_html}</div>'
        '</div>'
    )
