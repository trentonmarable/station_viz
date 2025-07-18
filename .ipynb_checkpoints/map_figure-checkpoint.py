# map_figure.py
import pandas as pd
import plotly.express as px

def generate_map_figure(selected_chargers, selected_teslas):
    df = pd.read_csv("all_stations.csv", low_memory=False)
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] == df['date'].max()].copy()

    # Filter and preprocess
    df = df[(df['rate'] > 0) & (df['rate'] < df['rate'].quantile(0.99))]
    df['tesla'] = (df['ev_network'] == "Tesla").astype(int)
    df['charger_type'] = df['dcfc'].map({1: 'DCFC', 0: 'Level 2'})
    df['tesla_type'] = df['tesla'].map({1: 'Tesla', 0: 'Non-Tesla'})

    # Apply filters
    df = df[
        df['charger_type'].isin(selected_chargers) &
        df['tesla_type'].isin(selected_teslas)
    ].copy()

    # Compute price_cents and hover text
    df["price_cents"] = (df["rate"] * 100).round(0)

    df["hover_text"] = (
        df["price_cents"].astype(str) + "¢/kWh<br>" +
        "(" + df["latitude"].round(7).astype(str) + ", " + df["longitude"].round(7).astype(str) + ")<br>" +
        "Network: " + df["ev_network"].fillna("Unknown") + "<br>" +
        "State: " + df["state"]
    )

    fig = px.scatter_mapbox(
        df,
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
        height=500,
        coloraxis_colorbar=dict(title="¢/kWh")
    )

    return fig
