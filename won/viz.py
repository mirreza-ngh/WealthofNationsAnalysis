import matplotlib.pyplot as plt
import plotly.express as px
import pandas as pd


def timeseries(df: pd.DataFrame, iso3c: str, y: str, title: str = ""):
    """Matplotlib time series for one country and one indicator."""
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
    hover: str = "country",
    title: str = ""
):
    """Plotly scatter with OLS trendline (statsmodels required)."""
    d = df.copy()

    # ✅ IMPORTANT: remove duplicate columns (fixes narwhals DuplicateError)
    d = d.loc[:, ~d.columns.duplicated()]

    d[x] = pd.to_numeric(d[x], errors="coerce")
    d[y] = pd.to_numeric(d[y], errors="coerce")
    d = d.dropna(subset=[x, y])

    return px.scatter(
        d,
        x=x,
        y=y,
        hover_name=hover if hover in d.columns else "iso3c",
        trendline="ols",
        title=title or f"{y} vs {x}"
    )


def choropleth_latest(df_latest: pd.DataFrame, value_col: str, title: str = ""):
    """Plotly choropleth with ISO3 cleaning + NaN dropping."""
    d = df_latest.copy()

    d["iso3c"] = d["iso3c"].astype(str).str.strip().str.upper()
    d = d[d["iso3c"].str.len() == 3]

    d[value_col] = pd.to_numeric(d[value_col], errors="coerce")
    d = d.dropna(subset=[value_col])

    if d.empty:
        return px.choropleth(title="No data available for this indicator")

    return px.choropleth(
        d,
        locations="iso3c",
        locationmode="ISO-3",
        color=value_col,
        color_continuous_scale="Viridis",
        hover_name="country" if "country" in d.columns else None,
        title=title or f"{value_col} (latest)"
    )
