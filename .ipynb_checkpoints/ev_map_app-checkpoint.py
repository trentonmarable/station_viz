import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import os
import glob
import re

# Load latest dataset
files = glob.glob("stations_*.csv")
dates = [re.findall(r"stations_(\d{8})\.csv", f) for f in files]
dates = [d[0] for d in dates if d]
latest_date = max(dates)
df = pd.read_csv(f"stations_{latest_date}.csv", low_memory=False)

# Clean + prep
df = df[(df['station_rate'] > 0) & (df['station_rate'] < df['station_rate'].quantile(0.99))]
df['charger_type'] = df['dcfc'].map({1: 'DCFC', 0: 'Level 2'})
df['tesla_type'] = df['tesla'].map({1: 'Tesla', 0: 'Non-Tesla'})

# Initialize Dash app
app = dash.Dash(__name__)
app.title = f"Prices in $/kWh — {latest_date[:4]}-{latest_date[4:6]}-{latest_date[6:]}"
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>body { margin: 0; overflow: hidden; }</style>
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
    html.H2("EV Charging Station Prices (Weekly Map)", style={"margin-bottom": "10px"}),

    html.Div([
        html.Label("Charger Type:"),
        dcc.Checklist(
            id='charger-filter',
            options=[{"label": x, "value": x} for x in df['charger_type'].unique()],
            value=['DCFC', 'Level 2'],
            labelStyle={'display': 'inline-block', 'margin-right': '15px'}
        ),
    ], style={'margin-bottom': '5px'}),

    html.Div([
        html.Label("Tesla Status:"),
        dcc.Checklist(
            id='tesla-filter',
            options=[{"label": x, "value": x} for x in df['tesla_type'].unique()],
            value=['Tesla', 'Non-Tesla'],
            labelStyle={'display': 'inline-block', 'margin-right': '15px'}
        ),
    ], style={'margin-bottom': '5px'}),

    dcc.Graph(
        id='price-map',
        config={"scrollZoom": True, "displayModeBar": False},
        style={"height": "calc(100vh - 150px)", "width": "100%"}
    )
], style={"margin": "0px", "padding": "10px"})

# Callback
@app.callback(
    Output("price-map", "figure"),
    Input("charger-filter", "value"),
    Input("tesla-filter", "value")
)
def update_map(selected_chargers, selected_tesla):
    filtered = df[
        df['charger_type'].isin(selected_chargers) &
        df['tesla_type'].isin(selected_tesla)
    ].copy()

    filtered["hover_text"] = (
        "$" + filtered["station_rate"].round(2).astype(str) + "/kWh<br>" +
        "(" + filtered["latitude"].round(7).astype(str) + ", " + filtered["longitude"].round(7).astype(str) + ")<br>" +
        "Network: " + filtered["ev_network"].fillna("Unknown") + "<br>" +
        "State: " + filtered["state"]
    )

    fig = px.scatter_mapbox(
        filtered,
        lat="latitude",
        lon="longitude",
        color="station_rate",
        color_continuous_scale="Viridis",
        hover_name="hover_text",
        hover_data={"station_rate": False, "latitude": False, "longitude": False, "state": False, "city": False, "ev_network": False},
        zoom=3
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title="")
    )

    return fig

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=False)
