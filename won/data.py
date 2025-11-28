import requests
import pandas as pd


def fetch_indicator(indicator: str, date: str = "1960:2023") -> pd.DataFrame:
    """Fetch one World Bank indicator as a tidy DataFrame: iso3c, country, year, value."""
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

        # WB error payload
        if isinstance(payload, dict) and "message" in payload:
            raise ValueError(payload["message"])

        meta, items = payload[0], payload[1]
        if items is None:
            break

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

    # clean iso3c hard + keep only REAL countries
    df["iso3c"] = df["iso3c"].astype(str).str.strip().str.upper()
    df = df[df["iso3c"].str.fullmatch(r"[A-Z]{3}")]

    # numeric values
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df


def fetch_many(indicators: dict, date: str = "1960:2023") -> pd.DataFrame:
    """
    Merge multiple indicators wide by (iso3c, year).
    Keep country from first indicator only.
    Force all indicator columns to numeric after merge.
    """
    frames = []
    for col, code in indicators.items():
        dfi = fetch_indicator(code, date).rename(columns={"value": col})
        frames.append(dfi)

    if not frames or all(f.empty for f in frames):
        return pd.DataFrame(columns=["iso3c", "country", "year"] + list(indicators.keys()))

    # start from first non-empty frame
    out = None
    for f in frames:
        if not f.empty:
            out = f
            break

    # merge rest
    for f in frames:
        if f is out or f.empty:
            continue

        if "country" in f.columns:
            f = f.drop(columns=["country"])

        out = out.merge(f, on=["iso3c", "year"], how="outer")

    # FORCE numeric for every indicator column
    for col in indicators.keys():
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")

    return out.sort_values(["iso3c", "year"]).reset_index(drop=True)
