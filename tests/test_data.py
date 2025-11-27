from won.data import fetch_many
from won.config import DEFAULT_INDICATORS

def test_fetch_many_has_columns():
    df = fetch_many(DEFAULT_INDICATORS, date="2019:2020")
    assert {"iso3c", "year"}.issubset(df.columns)
from won.transform import latest_complete
import pandas as pd

def test_latest_complete_picks_latest():
    df = pd.DataFrame({
        "iso3c": ["USA","USA","USA","ITA","ITA"],
        "year":  [2020, 2021, 2022, 2020, 2022],
        "gdp_pc":[1, None, 3, 5, 6],
        "life_exp":[10, 11, None, None, 20],
    })
    out = latest_complete(df, min_cols=1)
    usa_year = out[out.iso3c=="USA"]["year"].iloc[0]
    ita_year = out[out.iso3c=="ITA"]["year"].iloc[0]
    assert usa_year == 2022
    assert ita_year == 2022
