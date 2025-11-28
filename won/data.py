import requests
import pandas as pd
import time


def fetch_indicator(indicator: str, date: str = "1960:2023") -> pd.DataFrame:
    """Fetch one World Bank indicator as a tidy DataFrame: iso3c, country, year, value."""
    url = (
        f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"
        f"?date={date}&format=json&per_page=20000"
    )

    rows = []
    page = 1
    none_retries = 2  # cloud sometimes returns items=None briefly

    while True:
        r = requests.get(f"{url}&page={page}", timeout=60)
        r.raise_for_status()
        payload = r.json()

        if isinstance(payload, dict) and "message" in payload:
            raise ValueError(payload["message"])

        meta, items = payload[0], payload[1]

        # ---- minimal retry if items is None ----
        if items is None:
            if none_retries > 0:
                none_retries -= 1
                time.sleep(1)
                continue
            else:
                break
        # ---------------------------------------

        for it in items:
            cid = it["country"]["id"]
            if cid == "WLD":
                continue

            rows.append({
                "iso3c": cid,
                "country": it["country"]["value"],
                "year": int(it["date"]),
                "value": it["value"],
            })

        if page >= meta["pages"]:
            break
        page += 1

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # keep only real countries (drop aggregates)
    df = df[df["iso3c"].astype(str).str.len() == 3]

    return df


def fetch_many(indicators: dict, date: str = "1960:2023") -> pd.DataFrame:
    """Merge multiple indicators wide by (iso3c, year). Keep country from first indicator only."""
    frames = []

    for col, code in indicators.items():
        dfi = fetch_indicator(code, date).rename(columns={"value": col})
        frames.append(dfi)

    if not frames or all(f.empty for f in frames):
        return pd.DataFrame(columns=["iso3c", "country", "year"] + list(indicators.keys()))

    out = None
    for f in frames:
        if not f.empty:
            out = f
            break

    for f in frames:
        if f is out or f.empty:
            continue
        if "country" in f.columns:
            f = f.drop(columns=["country"])
        out = out.merge(f, on=["iso3c", "year"], how="outer")

    return out.sort_values(["iso3c", "year"]).reset_index(drop=True)
