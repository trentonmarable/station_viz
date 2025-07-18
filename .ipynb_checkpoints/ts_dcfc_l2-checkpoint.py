import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output
import os

# Load panel
df = pd.read_csv("all_stations.csv")

# Filter and preprocess
df = df[(df['rate'] > 0) & (df['rate'] < df['rate'].quantile(0.99))]
df['charger_type'] = df['dcfc'].map({1: 'DCFC', 0: 'Level 2'})
df['tesla'] = (df['ev_network'] == "Tesla").astype(int)
df['tesla_type'] = df['tesla'].map({1: 'Tesla', 0: 'Non-Tesla'})

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "Prices — Timeseries"
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

# Layout (no filters)
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

# Callback — dummy input to trigger on load
@app.callback(
    Output("price-trend", "figure"),
    Input("price-trend", "id")
)
def update_chart(_):
    df_copy = df.assign(
        charger_category=lambda d: d.apply(
            lambda row: (
                "Tesla DCFC" if row["dcfc"] == 1 and row["ev_network"] == "Tesla" else
                "Non-Tesla DCFC" if row["dcfc"] == 1 and row["ev_network"] != "Tesla" else
                "Level 2"
            ),
            axis=1
        )
    )

    grouped = (
        df_copy
        .groupby(["date", "charger_category"])["rate"]
        .mean()
        .unstack(fill_value=float("nan")) * 100
    )

    fig = go.Figure()

    if "Tesla DCFC" in grouped.columns:
        fig.add_trace(go.Scatter(
            x=grouped.index,
            y=grouped["Tesla DCFC"],
            mode='lines+markers',
            name='Tesla DCFC',
            line=dict(color='#FF0000'),
            marker=dict(color='#FF0000'),
            hovertemplate='Tesla DCFC: %{y:.1f}¢/kWh<extra></extra>'
        ))

    if "Non-Tesla DCFC" in grouped.columns:
        fig.add_trace(go.Scatter(
            x=grouped.index,
            y=grouped["Non-Tesla DCFC"],
            mode='lines+markers',
            name='Non-Tesla DCFC',
            line=dict(color='#DAA520'),
            marker=dict(color='#DAA520'),
            hovertemplate='Non-Tesla DCFC: %{y:.1f}¢/kWh<extra></extra>'
        ))

    if "Level 2" in grouped.columns:
        fig.add_trace(go.Scatter(
            x=grouped.index,
            y=grouped["Level 2"],
            mode='lines+markers',
            name='Level 2',
            line=dict(color='#1f77b4'),
            marker=dict(color='#1f77b4'),
            hovertemplate='Level 2: %{y:.1f}¢/kWh<extra></extra>'
        ))

    fig.update_layout(
        title={
            'text': "Average Charging Price Over Time<br>(By Charger Type)",
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
#python ev_ts_app.py
#Open http://localhost:8050
