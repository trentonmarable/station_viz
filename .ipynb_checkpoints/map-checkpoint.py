import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output
import os

# Load data
df_full = pd.read_csv("all_stations.csv", low_memory=False)

# Clean and filter to latest date
df_full['date'] = pd.to_datetime(df_full['date'])
latest_date = df_full['date'].max().strftime("%Y-%m-%d")
df = df_full[df_full['date'] == df_full['date'].max()].copy()

# Further cleaning
df = df[(df['rate'] > 0) & (df['rate'] < df['rate'].quantile(0.99))]
df['tesla'] = (df['ev_network'] == "Tesla").astype(int)
df['charger_type'] = df['dcfc'].map({1: 'DCFC', 0: 'Level 2'})
df['tesla_type'] = df['tesla'].map({1: 'Tesla', 0: 'Non-Tesla'})

# Initialize Dash app
app = dash.Dash(__name__)
app.title = f"Prices — {latest_date}"
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
    html.H2(
        f"Prices in ¢/kWh. Last updated: {latest_date}",
        style={"margin-bottom": "10px"}
    ),

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
        config={"scrollZoom": True, "displayModeBar": True},
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
    Output("price-map", "figure"),
    Input("charger-filter", "value"),
    Input("tesla-filter", "value")
)
def update_map(selected_chargers, selected_tesla):
    filtered = df[
        df['charger_type'].isin(selected_chargers) &
        df['tesla_type'].isin(selected_tesla)
    ].copy()

    filtered["price_cents"] = (filtered["rate"] * 100).round(0)

    filtered["hover_text"] = (
        filtered["price_cents"].astype(str) + "¢/kWh<br>" +
        "(" + filtered["latitude"].round(7).astype(str) + ", " + filtered["longitude"].round(7).astype(str) + ")<br>" +
        "Network: " + filtered["ev_network"].fillna("Unknown") + "<br>" +
        "State: " + filtered["state"]
    )

    fig = px.scatter_mapbox(
        filtered,
        lat="latitude",
        lon="longitude",
        color="price_cents",
        color_continuous_scale=px.colors.diverging.RdYlGn[::-1],
        custom_data=["latitude", "longitude", "ev_network", "state", "price_cents"],
        zoom=3
    )

    fig.update_traces(
        hovertemplate=
            "%{customdata[4]}¢/kWh<br>" +
            "(%{customdata[0]}, %{customdata[1]})<br>" +
            "Network: %{customdata[2]}<br>" +
            "State: %{customdata[3]}<extra></extra>"
    )

    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        coloraxis_colorbar=dict(title="¢/kWh")
    )

    return fig

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=True)







#cd C:\Users\tmarable\OneDrive - University of Tennessee\Documents\GitHub\station_viz
#python ev_map_app.py
#Open http://localhost:8050
