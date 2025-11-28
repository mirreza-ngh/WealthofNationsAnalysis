import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from won.config import DEFAULT_INDICATORS
from won.data import fetch_many
from won.transform import latest_complete, correlation_matrix
from won.viz import timeseries, scatter_rel, choropleth_latest

st.set_page_config(page_title="Wealth of Nations", page_icon="🌍", layout="wide")

st.title("🌍 Wealth of Nations — Interactive Dashboard")

# ---- Sidebar ----
st.sidebar.header("Settings")

date_range = st.sidebar.text_input("Year range", value="1960:2023")
selected_inds = st.sidebar.multiselect(
    "Indicators",
    options=list(DEFAULT_INDICATORS.keys()),
    default=list(DEFAULT_INDICATORS.keys())
)
min_cols = st.sidebar.slider("Min non-null indicators for latest table", 1, 4, 2)
reload_btn = st.sidebar.button("Load / Refresh data")

# ---- Load data ----
if reload_btn or "panel" not in st.session_state:
    if not selected_inds:
        st.warning("Select at least one indicator.")
    else:
        ind_dict = {k: DEFAULT_INDICATORS[k] for k in selected_inds}
        st.session_state["panel"] = fetch_many(ind_dict, date=date_range.strip())

panel = st.session_state.get("panel", pd.DataFrame())

st.subheader("Dataset preview")
st.write(f"Shape: {panel.shape}")
st.dataframe(panel.head(20), use_container_width=True)

if panel.empty:
    st.warning("No data loaded yet. Click 'Load / Refresh data' in the sidebar.")
    st.stop()

# ---- Latest complete ----
latest = latest_complete(panel, min_cols=min_cols)

for c in latest.columns:
    if c not in ("iso3c", "year", "country"):
        latest[c] = pd.to_numeric(latest[c], errors="coerce")

st.subheader("Latest complete values (by country)")
st.dataframe(latest.head(30), use_container_width=True)

st.subheader("Correlation matrix (latest)")
corr = correlation_matrix(latest)
st.dataframe(corr, use_container_width=True)

# ---- Visuals ----
st.header("Visualizations")
tab1, tab2, tab3 = st.tabs(["Time series", "Scatter", "Map"])

with tab1:
    st.subheader("Country time series")
    countries = sorted(panel["iso3c"].dropna().unique().tolist())
    iso3c = st.selectbox(
        "Country (ISO3)",
        countries,
        index=countries.index("USA") if "USA" in countries else 0
    )

    ind_cols_panel = [c for c in panel.columns if c not in ("iso3c", "year", "country")]
    y_col = st.selectbox("Indicator", ind_cols_panel)

    timeseries(panel, iso3c=iso3c, y=y_col, title=f"{y_col} — {iso3c}")
    st.pyplot(plt.gcf(), use_container_width=True)

with tab2:
    st.subheader("Scatter (latest)")
    ind_cols_latest = [c for c in latest.columns if c not in ("iso3c", "year", "country")]

    if len(ind_cols_latest) >= 2:
        x_col = st.selectbox("X", ind_cols_latest, index=0)
        y_col = st.selectbox("Y", ind_cols_latest, index=1)
        fig_sc = scatter_rel(
            latest,
            x=x_col,
            y=y_col,
            hover="country",
            title=f"{y_col} vs {x_col}"
        )
        st.plotly_chart(fig_sc, use_container_width=True)
    else:
        st.info("Need at least two indicators selected.")

with tab3:
    st.subheader("Map (latest available per country)")

    ind_cols_panel = [c for c in panel.columns if c not in ("iso3c", "year", "country")]
    map_col = st.selectbox("Indicator to map", ind_cols_panel)

    # IMPORTANT: force numeric BEFORE dropna
    panel[map_col] = pd.to_numeric(panel[map_col], errors="coerce")

    d = panel[["iso3c", "country", "year", map_col]].dropna(subset=[map_col])
    idx = d.groupby("iso3c")["year"].idxmax()
    map_df = d.loc[idx].reset_index(drop=True)

    fig_map = choropleth_latest(
        map_df,
        value_col=map_col,
        title=f"{map_col} (latest available)"
    )
    st.plotly_chart(fig_map, use_container_width=True)

st.caption("Data: World Bank Open Data API. App: Streamlit.")
