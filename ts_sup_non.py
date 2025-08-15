import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
import os

# Load panel
stations = pd.read_csv("all_stations.csv")

# Filter and preprocess
stations = stations[
    (stations['rate'] > 0) & 
    (stations['rate'] < stations['rate'].quantile(0.99))
]

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Prices — DCFC Breakdown"
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            html, body { margin: 0; padding: 0; height: 100%; overflow: hidden; }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Layout
app.layout = html.Div([
    dcc.Graph(
        id='price-trend',
        config={"scrollZoom": False, "displayModeBar": False},
        style={"flex": "1", "minHeight": "300px"}
    )
], style={
    "margin": "0px",
    "padding": "10px",
    "height": "100vh",
    "display": "flex",
    "flexDirection": "column",
    "overflow": "hidden"
})

# Callback
@app.callback(
    Output("price-trend", "figure"),
    Input("price-trend", "id")  # dummy input to trigger once
)
def update_chart(_):
    # Filter for DCFC stations
    tesla = stations[(stations["ev_network"] == "Tesla") & (stations["dcfc"] == 1)]
    nontesla = stations[(stations["ev_network"] != "Tesla") & (stations["dcfc"] == 1)]

    # Group and compute rates
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

    # Build figure
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=tesla_rate.index, y=tesla_rate.values,
        mode='lines+markers',
        name='Superchargers (Tesla vehicle)',
        line=dict(color='#8B0000'),
        marker=dict(color='#8B0000'),
        hovertemplate='%{y:.1f}¢/kWh<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=tesla_nrate.index, y=tesla_nrate.values,
        mode='lines+markers',
        name='Superchargers (Non-Tesla vehicle)',
        line=dict(color='#FF7F7F'),
        marker=dict(color='#FF7F7F'),
        hovertemplate='%{y:.1f}¢/kWh<extra></extra>'
    ))

    fig.add_trace(go.Scatter(
        x=nontesla_rate.index, y=nontesla_rate.values,
        mode='lines+markers',
        name='All other stations',
        line=dict(color='#1f77b4'),
        marker=dict(color='#1f77b4'),
        hovertemplate='%{y:.1f}¢/kWh<extra></extra>'
    ))

    fig.update_layout(
        title={
            'text': "Average DCFC Charging Prices Over Time",
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="Date",
        yaxis_title="Average Price (¢/kWh)",
        hovermode='x unified',
        width=1000,
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        xaxis=dict(showgrid=True, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridcolor='lightgray')
    )

    return fig

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=True)







#cd C:\Users\tmarable\OneDrive - University of Tennessee\Documents\GitHub\station_viz
#python ts_sup_non.py
#Open http://localhost:8050
