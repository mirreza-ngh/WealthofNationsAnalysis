import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from won.config import DEFAULT_INDICATORS
from won.data import fetch_many
from won.transform import latest_complete, correlation_matrix
from won.viz import timeseries, scatter_rel, choropleth_latest


st.set_page_config(
    page_title="Wealth of Nations",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍Wealth of Nations")
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

# remove any duplicate columns just in case cache/merge created some
panel = panel.loc[:, ~panel.columns.duplicated()]


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

# force numeric just in case cached values were strings
for c in latest.columns:
    if c not in ("iso3c", "year", "country"):
        latest[c] = pd.to_numeric(latest[c], errors="coerce")

latest = latest.loc[:, ~latest.columns.duplicated()]

st.subheader("Latest complete values (by country)")
st.dataframe(late
