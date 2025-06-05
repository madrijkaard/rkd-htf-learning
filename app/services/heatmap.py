import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from pathlib import Path

def generate_heatmap_data():
    bids_path = Path("data/bids/BTC.csv")
    asks_path = Path("data/asks/BTC.csv")

    df_bids = pd.read_csv(bids_path)
    df_asks = pd.read_csv(asks_path)

    df_bids["type"] = "bid"
    df_asks["type"] = "ask"

    df = pd.concat([df_bids, df_asks])
    df["price"] = df["price"].astype(float)
    df["amount"] = df["amount"].astype(float)

    # criar matriz de calor simplificada
    df_grouped = df.groupby(["price", "type"]).sum().reset_index()
    df_pivot = df_grouped.pivot(index="price", columns="type", values="amount").fillna(0)

    fig = go.Figure(data=go.Heatmap(
        z=[df_pivot["bid"].values.tolist(), df_pivot["ask"].values.tolist()],
        x=["bid", "ask"],
        y=df_pivot.index.tolist(),
        colorscale="Viridis",
        colorbar=dict(title="Volume")
    ))

    return pio.to_json(fig)
