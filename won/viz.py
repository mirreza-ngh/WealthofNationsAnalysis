import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd


def timeseries(df: pd.DataFrame, iso3c: str, y: str, title: str = ""):
    """
    Matplotlib time series for one country and one indicator.
    Draws on the current figure (Streamlit should use st.pyplot(plt.gcf())).
    """
    sub = df[df["iso3c"] == iso3c].sort_values("year")
    plt.figure()
    plt.plot(sub["year"], sub[y])
    plt.xlabel("Year")
    plt.ylabel(y)
    plt.title(title or f"{y} — {iso3c}")
    plt.tight_layout()


def scatter_rel(
    df: pd.DataFrame,
    x: str,
    y: str,
    hover: str = "iso3c",
    title: str = ""
):
    """
    Plotly scatter with OLS trendline (requires statsmodels installed).
    """
    # Ensure numeric for trendline + axes
    d = df.copy()
    d[x] = pd.to_numeric(d[x], errors="coerce")
    d[y] = pd.to_numeric(d[y], errors="coerce")
    d = d.dropna(subset=[x, y])

    return px.scatter(
        d,
        x=x,
        y=y,
        hover_name=hover,
        trendline="ols",
        title=title or f"{y} vs {x}"
    )


def choropleth_latest(
    df_latest: pd.DataFrame,
    value_col: str,
    title: str = ""
):
    """
    Plotly choropleth for latest values.
    Cleans iso3 codes + drops missing values so the map is never fully blank
    unless there is truly no data.
    """
    d = df_latest.copy()

    # --- Clean and validate iso3 codes ---
    d["iso3c"] = (
        d["iso3c"]
        .astype(str)
        .str.strip()
        .str.upper()
    )
    d = d[d["iso3c"].str.len() == 3]

    # --- Ensure numeric + drop missing for the mapped column ---
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce")
    d = d.dropna(subset=[value_col])

    # If still empty, return an empty map with a helpful title
    if d.empty:
        return px.choropleth(title="No data available for this indicator")

    return px.choropleth(
        d,
        locations="iso3c",
        locationmode="ISO-3",
        color=value_col,
        color_continuous_scale="Viridis",
        title=title or f"{value_col} (latest)"
    )
