# ts_dcfc_l2_figure.py
import pandas as pd
import plotly.graph_objects as go

def generate_dcfc_l2_figure():
    df = pd.read_csv("all_stations.csv")
    df = df[(df['rate'] > 0) & (df['rate'] < df['rate'].quantile(0.99))]
    df['charger_category'] = df.apply(
        lambda row: "DCFC (Tesla station)" if row['dcfc'] == 1 and row['ev_network'] == "Tesla"
        else "DCFC (Non-Tesla station)" if row['dcfc'] == 1
        else "Level 2",
        axis=1
    )

    grouped = (
        df.groupby(["date", "charger_category"])["rate"]
        .mean()
        .unstack(fill_value=float("nan")) * 100
    )

    fig = go.Figure()
    colors = {"DCFC (Tesla station)": "#FF0000", "DCFC (Non-Tesla station)": "#DAA520", "Level 2": "#1f77b4"}

    for col in grouped.columns:
        fig.add_trace(go.Scatter(
            x=grouped.index,
            y=grouped[col],
            mode='lines+markers',
            name=col,
            line=dict(color=colors[col]),
            marker=dict(color=colors[col]),
            hovertemplate=f'{col}: '+'%{y:.1f}¢/kWh<extra></extra>'
        ))

    fig.update_layout(
        title={'text': "DCFC vs Level 2", 'x': 0.5},
        xaxis_title="Date",
        yaxis_title="¢/kWh",
        height=500,
        hovermode="x unified"
    )
    return fig
