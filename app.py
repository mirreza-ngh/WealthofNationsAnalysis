import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
st.caption("Explore World Bank indicators: trends, relationships, and global patterns.")

# ---------------- Sidebar ----------------
st.sidebar.header("Data settings")

date_range = st.sidebar.text_input(
    "Year range",
    value="1960:2023",
    help="Format: start:end (example 1990:2023)",
)

indicator_keys = list(DEFAULT_INDICATORS.keys())
selected_inds = st.sidebar.multiselect(
    "Indicators",
    options=indicator_keys,
    default=indicator_keys,
)

min_cols = st.sidebar.slider(
    "Min non-null indicators (latest complete)",
    min_value=1,
    max_value=max(2, len(selected_inds)) if selected_inds else 2,
    value=2,
)

reload_btn = st.sidebar.button("Load / Refresh data")

# ---------------- Data loading ----------------
@st.cache_data(show_spinner=False)
def load_panel(ind_dict, date):
    return fetch_many(ind_dict, date=date)

if reload_btn or "panel" not in st.session_state:
    if not selected_inds:
        st.warning("Pick at least one indicator in the sidebar.")
        st.stop()

    selected_dict = {k: DEFAULT_INDICATORS[k] for k in selected_inds}

    with st.spinner("Fetching data from World Bank API…"):
        st.session_state["panel"] = load_panel(selected_dict, date_range)

panel = st.session_state["panel"]

# ---------------- Preview ----------------
st.subheader("Dataset preview")
st.write(
    f"Rows: **{len(panel):,}** | "
    f"Countries: **{panel['iso3c'].nunique():,}** | "
    f"Years: **{panel['year'].nunique():,}**"
)
st.dataframe(panel.head(20), use_container_width=True)

# ---------------- Latest complete ----------------
latest = latest_complete(panel, min_cols=min_cols)

# force numeric anyway (safe)
for c in latest.columns:
    if c not in ("iso3c", "year", "country"):
        latest[c] = pd.to_numeric(latest[c], errors="coerce")

st.subheader("Latest complete values (by country)")
st.dataframe(latest.head(50), use_container_width=True)

# ---------------- Correlation ----------------
st.subheader("Correlation matrix (latest complete)")
corr = correlation_matrix(latest)
st.dataframe(corr, use_container_width=True)

# ---------------- Visuals ----------------
st.markdown("---")
st.header("Visualizations")

tab1, tab2, tab3 = st.tabs(["Time series", "Scatter", "Map"])

with tab1:
    st.subheader("Country time series")
    countries = sorted(panel["iso3c"].dropna().unique().tolist())
    default_country = "USA" if "USA" in countries else countries[0]

    iso3c = st.selectbox("Country (ISO3)", countries, index=countries.index(default_country))

    numeric_cols_panel = [c for c in panel.columns if c not in ("iso3c", "year", "country")]
    y_col = st.selectbox("Indicator", numeric_cols_panel)

    timeseries(panel, iso3c=iso3c, y=y_col, title=f"{y_col} — {iso3c}")
    st.pyplot(plt.gcf(), use_container_width=True)

with tab2:
    st.subheader("Relationship scatter (latest)")
    numeric_cols_latest = [
        c for c in latest.columns
        if c not in ("iso3c", "year", "country")
        and pd.api.types.is_numeric_dtype(latest[c])
    ]

    if len(numeric_cols_latest) < 2:
        st.info("Need at least two numeric indicators to make a scatter plot.")
    else:
        x_col = st.selectbox("X axis", numeric_cols_latest, index=0)
        y_col = st.selectbox("Y axis", numeric_cols_latest, index=1)

        fig_sc = scatter_rel(
            latest,
            x=x_col,
            y=y_col,
            hover="country",
            title=f"{y_col} vs {x_col} (latest complete)"
        )
        st.plotly_chart(fig_sc, use_container_width=True)

with tab3:
    st.subheader("Choropleth (latest available per country)")

    numeric_cols_panel = [c for c in panel.columns if c not in ("iso3c", "year", "country")]
    map_col = st.selectbox("Indicator to map", numeric_cols_panel)

    # latest non-null per country for THIS indicator
    d = panel[["iso3c", "country", "year", map_col]].dropna(subset=[map_col])
    idx = d.groupby("iso3c")["year"].idxmax()
    map_df = d.loc[idx].reset_index(drop=True)

    fig_map = choropleth_latest(
        map_df,
        value_col=map_col,
        title=f"{map_col} (latest available)"
    )
    st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")
st.caption("Data: World Bank Open Data API. App: Streamlit.")
