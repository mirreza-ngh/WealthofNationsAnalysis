import requests
import pandas as pd


def fetch_indicator(indicator: str, date: str = "1960:2023") -> pd.DataFrame:
    """Fetch one World Bank indicator as tidy DataFrame: iso3c, country, year, value."""
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

        if len(payload) < 2 or payload[1] is None:
            break

        meta, items = payload[0], payload[1]

        for it in items:
            cid = it["country"]["id"]
            if cid == "WLD":
                continue

            rows.append({
                "iso3c": cid.strip().upper(),
                "country": it["country"]["value"],
                "year": int(it["date"]),
                "value": it["value"],
            })

        if page >= meta.get("pages", 1):
            break
        page += 1

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # numeric values
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # keep only real ISO-3 countries
    df = df[df["iso3c"].str.len() == 3]

    return df


def fetch_many(indicators: dict, date: str = "1960:2023") -> pd.DataFrame:
    """
    Fetch multiple indicators and merge wide on (iso3c, year).
    Country name is kept from the first indicator only (avoids duplicates).
    Robust if any indicator returns empty.
    """
    out = None

    for col, code in indicators.items():
        dfi = fetch_indicator(code, date)
        if dfi.empty:
            continue

        dfi = dfi.rename(columns={"value": col})

        # after first indicator, drop country col before merging (prevents duplicates)
        if out is not None and "country" in dfi.columns:
            dfi = dfi.drop(columns=["country"])

        out = dfi if out is None else out.merge(dfi, on=["iso3c", "year"], how="outer")

    if out is None:
        return pd.DataFrame(columns=["iso3c", "country", "year"] + list(indicators.keys()))

    return out.sort_values(["iso3c", "year"]).reset_index(drop=True)
