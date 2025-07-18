import dash
from dash import dcc, html, Input, Output
import os
import pandas as pd
from map_figure import generate_map_figure
from ts_dcfc_l2_figure import generate_dcfc_l2_figure
from ts_sup_non_figure import generate_sup_non_figure

# Load full dataset once for filter options and date
df = pd.read_csv("all_stations.csv")
df['date'] = pd.to_datetime(df['date'])
latest_date = df['date'].max().strftime("%Y-%m-%d")

# Get filter options
df_latest = df[df['date'] == df['date'].max()].copy()
df_latest['tesla'] = (df_latest['ev_network'] == "Tesla").astype(int)
df_latest['charger_type'] = df_latest['dcfc'].map({1: 'DCFC', 0: 'Level 2'})
df_latest['tesla_type'] = df_latest['tesla'].map({1: 'Tesla', 0: 'Non-Tesla'})

# Initialize app
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
            html, body { margin: 0; padding: 0; height: 100%; overflow-x: hidden; }
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
    html.H2(f"Prices in ¢/kWh from {latest_date}", style={"margin-bottom": "10px"}),

    html.Div([
        html.Label("Charger Type:"),
        dcc.Checklist(
            id='charger-filter',
            options=[{"label": x, "value": x} for x in sorted(df_latest['charger_type'].unique())],
            value=sorted(df_latest['charger_type'].unique()),
            labelStyle={'display': 'inline-block', 'margin-right': '15px'}
        ),
        html.Label("Tesla Status:"),
        dcc.Checklist(
            id='tesla-filter',
            options=[{"label": x, "value": x} for x in sorted(df_latest['tesla_type'].unique())],
            value=sorted(df_latest['tesla_type'].unique()),
            labelStyle={'display': 'inline-block', 'margin-right': '15px'}
        ),
    ], style={"margin-bottom": "10px"}),

    dcc.Graph(id="price-map", config={"scrollZoom": True, "displayModeBar": True}),

    html.Hr(),

    html.H2("Average Prices Over Time", style={"margin-top": "30px", "margin-bottom": "10px"}),
    
    dcc.Graph(id="ts-dcfc-l2", figure=generate_dcfc_l2_figure(), config={"displayModeBar": False}),
    dcc.Graph(id="ts-sup-non", figure=generate_sup_non_figure(), config={"displayModeBar": False}),
], style={"padding": "15px", "maxWidth": "1000px", "margin": "auto"})

# Callback — only updates the map
@app.callback(
    Output("price-map", "figure"),
    Input("charger-filter", "value"),
    Input("tesla-filter", "value")
)
def update_map(selected_chargers, selected_teslas):
    return generate_map_figure(selected_chargers, selected_teslas)

# Run app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8050)), debug=True)
