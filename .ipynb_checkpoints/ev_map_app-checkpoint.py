import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import os
import glob
import re

# Load the weekly dataset
files = glob.glob("stations_*.csv")
dates = [re.findall(r"stations_(\d{8})\.csv", f) for f in files]
dates = [d[0] for d in dates if d]
latest_date = max(dates)
latest_file = f"stations_{latest_date}.csv"

# Load the latest file
df = pd.read_csv(latest_file, low_memory=False)

# Filter: remove zero/free prices and extreme outliers
df = df[(df['station_rate'] > 0) & (df['station_rate'] < df['station_rate'].quantile(0.99))]

# Add readable charger type
df['charger_type'] = df['dcfc'].map({1: 'DCFC', 0: 'Level 2'})

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "EV Charging Station Prices"

# Layout
app.layout = html.Div([
    html.H2("EV Charging Station Prices (Weekly Map)"),
    dcc.RadioItems(
        id='charger-filter',
        options=[
            {"label": "DCFC", "value": "DCFC"},
            {"label": "Level 2", "value": "Level 2"}
        ],
        value="DCFC",
        labelStyle={'display': 'inline-block', 'margin-right': '20px'}
    ),
    dcc.Graph(id='price-map')
])

# Callback
@app.callback(
    Output("price-map", "figure"),
    Input("charger-filter", "value")
)
def update_map(charger_type):
    filtered = df[df["charger_type"] == charger_type]

    fig = px.scatter_mapbox(
        filtered,
        lat="latitude",
        lon="longitude",
        color="station_rate",
        color_continuous_scale="Viridis",
        hover_data={"station_rate": True},
        zoom=4,
        height=700
    )
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title="Price ($/kWh)"),
        scrollZoom=True
    )
    return fig

# Run the server
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8050)),  # 8050 is fallback for local dev
        debug=True
    )