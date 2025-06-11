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
    if not {"timestamp", "datetime_local", "price", "volume", "current_price"}.issubset(df.columns):
        raise ValueError("Arquivo CSV inválido")

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df["datetime_local"] = pd.to_datetime(df["datetime_local"])
    df["price"] = pd.to_numeric(df["price"])
    df["volume"] = pd.to_numeric(df["volume"])
    df["current_price"] = pd.to_numeric(df["current_price"])

    if minutes_back > 0:
        time_limit = datetime.utcnow() - timedelta(minutes=minutes_back)
        df = df[df["timestamp"] >= time_limit]

    return df


def _create_histogram(df: pd.DataFrame, title_base: str, side: str, top: int = None, bucket_size: float = 100.0):
    if df.empty:
        return f"<p style='color:red;'>{title_base} – Dados insuficientes</p>"

    df["price_bucket"] = (df["price"] // bucket_size) * bucket_size
    grouped = df.groupby("price_bucket")["volume"].sum().reset_index()

    latest = df.sort_values("datetime_local", ascending=False).iloc[0]
    current_price = latest["current_price"]
    current_bucket = (current_price // bucket_size) * bucket_size

    if top:
        grouped = grouped.nlargest(top, "volume")

    grouped = grouped.sort_values("price_bucket")

    # Define cores com base no lado (ASK ou BID)
    colors = []
    for pb in grouped["price_bucket"]:
        if abs(pb - current_bucket) < 1e-8:
            colors.append("yellow")  # current price
        elif side == "ASK" and pb > current_bucket:
            colors.append("red")     # resistência
        elif side == "BID" and pb < current_bucket:
            colors.append("green")   # suporte
        else:
            colors.append("indigo")  # neutro

    min_time = df["datetime_local"].min()
    legenda_tempo = min_time.strftime("desde %H:%M do dia %d/%m")

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"{p:.2f}" for p in grouped["price_bucket"]],
        y=grouped["volume"],
        marker_color=colors
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


def generate_histograms(symbol: str, top: int = None, minutes: int = 60, bucket_size: float = 100.0):
    """
    Gera histogramas de liquidez para bids e asks.
    - symbol: símbolo da cripto, ex: BTC
    - top: número de maiores barras a exibir
    - minutes: tempo de histórico a considerar (0 = todos)
    - bucket_size: tamanho do intervalo de preço para cada barra
    """
    bids_path = Path(f"data/bids/{symbol}.csv")
    asks_path = Path(f"data/asks/{symbol}.csv")

    bids_df = _load_filtered_data(bids_path, minutes_back=minutes)
    asks_df = _load_filtered_data(asks_path, minutes_back=minutes)

    bids_hist = _create_histogram(bids_df, f"Histograma de Liquidez – BIDS ({symbol})", side="BID", top=top, bucket_size=bucket_size)
    asks_hist = _create_histogram(asks_df, f"Histograma de Liquidez – ASKS ({symbol})", side="ASK", top=top, bucket_size=bucket_size)

    return (
        '<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>'
        '<div style="display: flex; flex-direction: column; gap: 30px; padding: 20px;">'
        f'{asks_hist}'
        f'{bids_hist}'
        '</div>'
    )
