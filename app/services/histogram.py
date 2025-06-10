from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio


def _load_filtered_data(file_path: Path, minutes_back: int = 60) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    df = pd.read_csv(file_path)
    if not {"timestamp", "datetime_local", "price", "volume"}.issubset(df.columns):
        raise ValueError("Arquivo CSV inválido")

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df["datetime_local"] = pd.to_datetime(df["datetime_local"])
    df["price"] = pd.to_numeric(df["price"])
    df["volume"] = pd.to_numeric(df["volume"])

    # Aplica filtro apenas se minutes_back > 0
    if minutes_back > 0:
        time_limit = datetime.utcnow() - timedelta(minutes=minutes_back)
        df = df[df["timestamp"] >= time_limit]

    return df


def _create_histogram(df: pd.DataFrame, title_base: str, top: int = None):
    if df.empty:
        return f"<p style='color:red;'>{title_base} – Dados insuficientes</p>"

    # Define o tamanho do bucket automaticamente (50 buckets)
    bucket_size = (df["price"].max() - df["price"].min()) / 50
    bucket_size = max(bucket_size, 0.01)  # Evita divisão por zero ou buckets minúsculos

    df["price_bucket"] = (df["price"] // bucket_size) * bucket_size
    grouped = df.groupby("price_bucket")["volume"].sum().reset_index()

    if top:
        grouped = grouped.nlargest(top, "volume")

    grouped = grouped.sort_values("price_bucket")

    # ⏰ Usa datetime_local mais antigo para legenda
    min_time = df["datetime_local"].min()
    legenda_tempo = min_time.strftime("desde %H:%M do dia %d/%m")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"{p:.2f}" for p in grouped["price_bucket"]],
        y=grouped["volume"],
        marker_color="indigo"
    ))

    fig.update_layout(
        title=f"{title_base} {legenda_tempo}",
        xaxis_title="Faixa de Preço",
        yaxis_title="Volume Total",
        xaxis=dict(type="category"),
        template="plotly_white",
        height=400
    )

    return pio.to_html(fig, full_html=False)


def generate_histograms(symbol: str, top: int = None, minutes: int = 60):
    bids_path = Path(f"data/bids/{symbol}.csv")
    asks_path = Path(f"data/asks/{symbol}.csv")

    bids_df = _load_filtered_data(bids_path, minutes_back=minutes)
    asks_df = _load_filtered_data(asks_path, minutes_back=minutes)

    bids_hist = _create_histogram(bids_df, f"Histograma de Liquidez – BIDS ({symbol})", top=top)
    asks_hist = _create_histogram(asks_df, f"Histograma de Liquidez – ASKS ({symbol})", top=top)

    return (
        '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'
        '<div style="display: flex; flex-direction: column; gap: 30px; padding: 20px;">'
        f'{asks_hist}'
        f'{bids_hist}'
        '</div>'
    )
