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
    """Carrega e prepara dados de uma pasta"""
    try:
        folder_path = Path(folder)
        csv_files = list(folder_path.glob("*.csv"))
        
        if not csv_files:
            return None, "Nenhum arquivo CSV encontrado", None
        
        df = pd.read_csv(csv_files[0])
        df = df[["timestamp", "price", "volume"]].copy()
        
        # Converter tipos
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit='s')
        df["price"] = pd.to_numeric(df["price"])
        df["volume"] = pd.to_numeric(df["volume"])
        
        # Calcular faixas de preço (0.5% do preço médio)
        avg_price = df["price"].mean()
        df["price_bucket"] = (df["price"] / (avg_price * 0.005)).round() * (avg_price * 0.005)
        
        # Agrupar tempo em intervalos de 5 minutos
        df["time_bucket"] = df["timestamp"].dt.floor("5min")
        
        return df, None, avg_price
        
    except Exception as e:
        logger.error(f"Erro ao carregar dados: {str(e)}")
        return None, f"Erro: {str(e)}", None

def _create_heatmap(df: pd.DataFrame, title: str, avg_price: float):
    """Cria um heatmap a partir de um DataFrame"""
    try:
        if df.empty:
            return "<p style='color:red;'>Dados vazios</p>"
            
        # Agrupar e pivotar
        pivot = df.groupby(["price_bucket", "time_bucket"])["volume"].mean().unstack(fill_value=0)
        pivot = pivot.sort_index(ascending=False)
        
        # Normalizar dados
        z_data = pivot.values
        z_data = (z_data - np.min(z_data)) / (np.max(z_data) - np.min(z_data) + 0.001)
        z_data = np.nan_to_num(z_data, nan=0, posinf=1, neginf=0)
        
        # Criar heatmap
        fig = go.Figure(go.Heatmap(
            z=z_data,
            x=pivot.columns.strftime("%H:%M"),
            y=[f"{p:.2f}" for p in pivot.index],
            colorscale='Viridis',
            zmin=0,
            zmax=1
        ))
        
        fig.update_layout(
            title=f"{title} (Preço Médio: {avg_price:.2f})",
            xaxis_title="Tempo",
            yaxis_title="Faixa de Preço",
            height=600
        )
        
        return pio.to_html(fig, full_html=False)
        
    except Exception as e:
        return f"<p style='color:red;'>Erro: {str(e)}</p>"

def generate_heatmap_data():
    """Gera os heatmaps e gráfico de debug"""
    # Carregar dados
    bids_df, bids_err, bids_avg = _load_and_prepare_data("data/bids")
    asks_df, asks_err, asks_avg = _load_and_prepare_data("data/asks")
    
    # Gerar heatmaps
    bids_html = _create_heatmap(bids_df, "Bids", bids_avg) if bids_df is not None else bids_err
    asks_html = _create_heatmap(asks_df, "Asks", asks_avg) if asks_df is not None else asks_err
    
    return (
        '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'
        '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px;">'
        f'<div>{bids_html}</div>'
        f'<div>{asks_html}</div>'
        '</div>'
    )