import streamlit as st
import pandas as pd

from won.config import DEFAULT_INDICATORS
from won.data import fetch_many
from won.transform import latest_complete, correlation_matrix
from won.viz import timeseries, scatter_rel, choropleth_latest

st.set_page_config(
    page_title="Wealth of Nations Dashboard",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 Wealth of Nations — Interactive Dashboard")
st.caption(
    "World Bank indicators: explore trends, relationships, and global patterns."
)

# -----------------------------
# Sidebar controls
# -----------------------------
st.sidebar.header("Data settings")

date_range = st.sidebar.text_input(
    "Year range (World Bank format)",
    value="1960:2023",
    help="Example: 1990:2023",
)

indicators = st.sidebar.multiselect(
    "Indicators to load",
    options=list(DEFAULT_INDICATORS.keys()),
    default=list(DEFAULT_INDICATORS.keys()),
    help="Pick which indicators to include in the analysis.",
)

min_cols = st.sidebar.slider(
    "Minimum non-null indicators for 'latest complete' dataset",
    min_value=1,
    max_value=max(2, len(indicators)),
    value=2,
)

load_btn = st.sidebar.button("Load / Refresh data")

# -----------------------------
# Data loading (cached)
# -----------------------------
@st.cache_data(show_spinner=False)
def load_panel(ind_list, date):
    return fetch_many(ind_list, date=date)

if load_btn or "panel" not in st.session_state:
    if len(indicators) == 0:
        st.warning("Please select at least one indicator.")
        st.stop()

    with st.spinner("Fetching data from World Bank API..."):
        panel = load_panel(indicators, date_range)
        st.session_state["panel"] = panel

panel = st.session_state["panel"]

# Basic sanity info
st.subheader("Dataset preview")
st.write(
    f"Rows: **{len(panel):,}**  |  "
    f"Countries: **{panel['iso3c'].nunique():,}**  |  "
    f"Years: **{panel['year'].nunique():,}**"
)
st.dataframe(panel.head(20), use_container_width=True)

# -----------------------------
# Latest complete slice
# -----------------------------
latest = latest_complete(panel, min_cols=min_cols)

st.subheader("Latest complete values (by country)")
st.dataframe(latest.head(20), use_container_width=True)

# -----------------------------
# Correlation matrix
# -----------------------------
st.subheader("Correlation matrix (latest complete)")
corr = correlation_matrix(latest)

# If your function returns a DataFrame, show it directly.
# If it returns something else, this still works as long as it's table-like.
st.dataframe(corr, use_container_width=True)

# -----------------------------
# Visualizations section
# -----------------------------
st.markdown("---")
st.header("Visualizations")

tab1, tab2, tab3 = st.tabs(["Time series", "Scatter", "Map"])

# ---- Time series tab ----
with tab1:
    st.subheader("Country time series")
    countries = sorted(panel["iso3c"].dropna().unique().tolist())
    default_country = "USA" if "USA" in countries else countries[0]

    iso3c = st.selectbox("Country (ISO3)", countries, index=countries.index(default_country))
    y_col = st.selectbox("Indicator", latest.columns.drop(["iso3c", "country", "year"], errors="ignore"))

    fig_ts = timeseries(panel, iso3c=iso3c, y=y_col, title=f"{y_col} — {iso3c}")
    # Your viz functions look Plotly-based (.show() in notebook),
    # so Streamlit can render them via st.plotly_chart:
    st.plotly_chart(fig_ts, use_container_width=True)

# ---- Scatter tab ----
with tab2:
    st.subheader("Relationship scatter (latest)")
    numeric_cols = [
        c for c in latest.columns
        if c not in ("iso3c", "country", "year")
        and pd.api.types.is_numeric_dtype(latest[c])
    ]
    if len(numeric_cols) < 2:
        st.info("Need at least two numeric indicators for scatter.")
    else:
        x_col = st.selectbox("X axis", numeric_cols, index=0)
        y_col = st.selectbox("Y axis", numeric_cols, index=1)

        fig_sc = scatter_rel(
            latest,
            x=x_col,
            y=y_col,
            title=f"{y_col} vs {x_col} (latest complete)"
        )
        st.plotly_chart(fig_sc, use_container_width=True)

# ---- Map tab ----
with tab3:
    st.subheader("Choropleth (latest)")
    map_col = st.selectbox("Indicator to map", numeric_cols if len(numeric_cols) else latest.columns)

    fig_map = choropleth_latest(
        latest,
        value_col=map_col,
        title=f"{map_col} (latest complete)"
    )
    st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")
st.caption("Data source: World Bank Open Data API. Built with Streamlit.")
