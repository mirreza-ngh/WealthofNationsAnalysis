import streamlit as st
import pandas as pd
import requests

from won.config import DEFAULT_INDICATORS
from won.data import fetch_many

st.set_page_config(page_title="Wealth of Nations DEBUG", page_icon="🛠️", layout="wide")
st.title("🛠️ Wealth of Nations — DEBUG MODE")

st.sidebar.header("Settings")
date_range = st.sidebar.text_input("Year range", value="1960:2023")
selected_inds = st.sidebar.multiselect(
    "Indicators",
    options=list(DEFAULT_INDICATORS.keys()),
    default=list(DEFAULT_INDICATORS.keys())
)
reload_btn = st.sidebar.button("Load / Refresh data")

# ----------------- RAW API CHECK -----------------
st.subheader("1) Raw World Bank API check")

if not selected_inds:
    st.warning("Select at least one indicator.")
    st.stop()

first_key = selected_inds[0]
first_code = DEFAULT_INDICATORS[first_key]

raw_url = (
    f"https://api.worldbank.org/v2/country/all/indicator/{first_code}"
    f"?date={date_range.strip()}&format=json&per_page=50&page=1"
)

st.write("Testing URL:")
st.code(raw_url)

try:
    r = requests.get(raw_url, timeout=30)
    st.write("Status code:", r.status_code)
    st.write("First 500 chars of response:")
    st.code(r.text[:500])

    # Try json parse
    j = r.json()
    st.write("JSON type:", type(j))
    if isinstance(j, list) and len(j) > 1:
        st.write("Meta keys:", list(j[0].keys()))
        st.write("Items length on page 1:", 0 if j[1] is None else len(j[1]))
    else:
        st.write("JSON content (truncated):")
        st.write(j)

except Exception as e:
    st.error(f"RAW API call failed: {e}")
    st.stop()

# ----------------- YOUR PIPELINE -----------------
st.subheader("2) Your fetch_many result")

if reload_btn or "panel" not in st.session_state:
    ind_dict = {k: DEFAULT_INDICATORS[k] for k in selected_inds}
    st.session_state["panel"] = fetch_many(ind_dict, date=date_range.strip())

panel = st.session_state.get("panel", pd.DataFrame())
st.write("panel shape:", panel.shape)
st.dataframe(panel.head(20), use_container_width=True)
