import pandas as pd
import plotly.graph_objects as go

def generate_sup_non_figure():
    df = pd.read_csv("all_stations.csv")

    # Filter only DCFC stations
    tesla = df[(df["ev_network"] == "Tesla") & (df["dcfc"] == 1)]
    nontesla = df[(df["ev_network"] != "Tesla") & (df["dcfc"] == 1)]

    # Compute means
    tesla_rate = (
        tesla[tesla["rate"].notna()]
        .groupby("date")["rate"]
        .mean() * 100
    )

    tesla_nrate = (
        tesla[tesla["n_rate"].notna()]
        .groupby("date")["n_rate"]
        .mean() * 100
    )

    nontesla_rate = (
        nontesla[nontesla["rate"].notna()]
        .groupby("date")["rate"]
        .mean() * 100
    )

    # Create plot
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=tesla_rate.index,
        y=tesla_rate.values,
        mode='lines+markers',
        name='Superchargers (Tesla vehicle)',
        line=dict(color='#8B0000'),
        marker=dict(color='#8B0000'),
        hovertemplate='Superchargers (Tesla vehicle): %{y:.1f}¢/kWh<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=tesla_nrate.index,
        y=tesla_nrate.values,
        mode='lines+markers',
        name='Superchargers (Non-Tesla vehicle)',
        line=dict(color='#FF7F7F'),
        marker=dict(color='#FF7F7F'),
        hovertemplate='Superchargers (Non-Tesla vehicle): %{y:.1f}¢/kWh<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=nontesla_rate.index,
        y=nontesla_rate.values,
        mode='lines+markers',
        name='All other stations',
        line=dict(color='#1f77b4'),
        marker=dict(color='#1f77b4'),
        hovertemplate='All other stations: %{y:.1f}¢/kWh<extra></extra>'
    ))

    fig.update_layout(
        title={'text': "Superchargers vs Non-Tesla DCFC", 'x': 0.5},
        xaxis_title="Date",
        yaxis_title="¢/kWh",
        height=500,
        hovermode="x unified"  # 👈 Add this line for shared hover
    )

    return fig
