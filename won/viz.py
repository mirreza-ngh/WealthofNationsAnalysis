import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd


def timeseries(df: pd.DataFrame, iso3c: str, y: str, title: str = ""):
    """
    Plot a time series for a single country's indicator.

    Parameters
    ----------
    df : pd.DataFrame
        Panel dataset with 'iso3c', 'year', and the selected indicator.
    iso3c : str
        ISO3 country code to plot.
    y : str
        Indicator column name.
    title : str, optional
        Plot title (auto-generated if blank).
    """
    sub = df[df["iso3c"] == iso3c].sort_values("year")
    plt.figure()
    plt.plot(sub["year"], sub[y])
    plt.xlabel("Year")
    plt.ylabel(sub[y], sub["Dollars"] )
    plt.title(title or f"{y} — {iso3c}")
    plt.tight_layout()


def scatter_rel(df: pd.DataFrame, x: str, y: str, hover: str = "iso3c", title: str = ""):
    """
    Create an interactive scatter plot with optional trendline.

    Parameters
    ----------
    df : pd.DataFrame
        Latest dataset with indicator columns.
    x, y : str
        Indicator names for axes.
    hover : str, default="iso3c"
        Column to show on hover tooltip if available.
    title : str, optional
        Plot title.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    hover_col = hover if hover in df.columns else "iso3c"
    return px.scatter(df, x=x, y=y, hover_name=hover_col, trendline="ols",
                      title=title or f"{y} vs {x}")


def choropleth_latest(df_latest: pd.DataFrame, value_col: str, title: str = ""):
    """
    Create a choropleth world map showing the latest available value per country.

    Parameters
    ----------
    df_latest : pd.DataFrame
        Data with exactly one row per country.
    value_col : str
        Column to map to the color scale.
    title : str, optional
        Map title.

    Returns
    -------
    plotly.graph_objects.Figure
    """
    d = df_latest.copy()
    d["iso3c"] = d["iso3c"].astype(str).str.strip().str.upper()
    d = d[d["iso3c"].str.len() == 3]
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce")
    d = d.dropna(subset=[value_col])

    return px.choropleth(
        d,
        locations="iso3c",
        locationmode="ISO-3",
        color=value_col,
        color_continuous_scale="Viridis",
        hover_name="country" if "country" in d.columns else None,
        title=title or f"{value_col} (latest)"
    )
