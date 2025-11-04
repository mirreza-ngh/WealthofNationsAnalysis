import requests
import pandas as pd

def fetch_indicator(indicator: str, date: str = "1960:2023") -> pd.DataFrame:
    """Fetch one World Bank indicator as a tidy DataFrame: country code, year, value."""
    url = (
        f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"
        f"?date={date}&format=json&per_page=20000"
    )
    rows = []
    page = 1
    while True:
        r = requests.get(f"{url}&page={page}", timeout=60)
        r.raise_for_status()
        payload = r.json()
        meta, items = payload[0], payload[1]
        for it in items:
            if it["country"]["id"] == "WLD":
                continue
            rows.append({
                "iso3c": it["country"]["id"],
                "year": int(it["date"]),
                "value": it["value"],
            })
        if page >= meta["pages"]:
            break
        page += 1
    return pd.DataFrame(rows)

def fetch_many(indicators: dict, date: str = "1960:2023") -> pd.DataFrame:
    """Merge multiple indicators wide by (iso3c, year)."""
    frames = []
    for col, code in indicators.items():
        dfi = fetch_indicator(code, date).rename(columns={"value": col})
        frames.append(dfi)
    out = frames[0]
    for dfi in frames[1:]:
        out = out.merge(dfi, on=["iso3c", "year"], how="outer")
    return out.sort_values(["iso3c", "year"]).reset_index(drop=True)
