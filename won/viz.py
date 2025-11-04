import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd

def timeseries(df: pd.DataFrame, iso3c: str, y: str, title: str = ""):
    sub = df[df["iso3c"] == iso3c].sort_values("year")
    plt.figure()
    plt.plot(sub["year"], sub[y])
    plt.xlabel("Year"); plt.ylabel(y)
    plt.title(title or f"{y} — {iso3c}")
    plt.tight_layout()

def scatter_rel(df: pd.DataFrame, x: str, y: str, hover: str = "iso3c", title: str = ""):
    return px.scatter(df, x=x, y=y, hover_name=hover, trendline="ols", title=title or f"{y} vs {x}")

def choropleth_latest(df_latest: pd.DataFrame, value_col: str, title: str = ""):
    return px.choropleth(
        df_latest, locations="iso3c", color=value_col,
        color_continuous_scale="Viridis", title=title or f"{value_col} (latest)"
    )
