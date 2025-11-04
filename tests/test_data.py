from won.data import fetch_many
from won.config import DEFAULT_INDICATORS

def test_fetch_many_has_columns():
    df = fetch_many(DEFAULT_INDICATORS, date="2019:2020")
    assert {"iso3c", "year"}.issubset(df.columns)
