import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd


def timeseries(df: pd.DataFrame, iso3c: str, y: str, title: str = ""):
    """Simple matplotlib line plot for one country and one indicator."""
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
    """Plotly scatter with optional OLS trendline (needs statsmodels)."""
    hover_col = hover if hover in df.columns else "iso3c"
    return px.scatter(
        df,
        x=x,
        y=y,
        hover_name=hover_col,
        trendline="ols",
        title=title or f"{y} vs {x}"
    )


def choropleth_latest(df_latest: pd.DataFrame, value_col: str, title: str = ""):
    """
    Plotly choropleth for latest values.
    Cleans ISO3 codes, forces numeric values, drops NaNs.
    If nothing is mappable, returns an empty figure with a clear title.
    """
    d = df_latest.copy()

    # clean iso codes and keep only real 3-letter countries
    d["iso3c"] = d["iso3c"].astype(str).str.strip().str.upper()
    d = d[d["iso3c"].str.len() == 3]

    # make sure values are numeric + drop missing
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce")
    d = d.dropna(subset=[value_col])

    if d.empty:
        return px.choropleth(title="No mappable data for this indicator")

    return px.choropleth(
        d,
        locations="iso3c",
        locationmode="ISO-3",
        color=value_col,
        color_continuous_scale="Viridis",
        hover_name="country" if "country" in d.columns else None,
        title=title or f"{value_col} (latest)"
    )
