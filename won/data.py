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

        # If WB sends an error object, stop clearly
        if isinstance(payload, dict) and "message" in payload:
            raise ValueError(payload["message"])

        meta, items = payload[0], payload[1]

        # If items is None, treat as empty and stop
        if items is None:
            break

        for it in items:
            cid = it["country"]["id"]
            if cid == "WLD":
                continue

            rows.append({
                "iso3c": cid,                       # keep as WB gives it
                "country": it["country"]["value"],  # full name
                "year": int(it["date"]),
                "value": it["value"],
            })

        if page >= meta["pages"]:
            break
        page += 1

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # Convert values to numeric (safe)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # KEEP ONLY REAL COUNTRIES (drop aggregates like 1A, EUU, SAS, etc.)
    df = df[df["iso3c"].astype(str).str.len() == 3]

    return df


def fetch_many(indicators: dict, date: str = "1960:2023") -> pd.DataFrame:
    """
    Merge multiple indicators wide by (iso3c, year).
    Keep country name from FIRST indicator only to avoid duplicate columns.
    """
    frames = []

    for col, code in indicators.items():
        dfi = fetch_indicator(code, date).rename(columns={"value": col})
        frames.append(dfi)

    # If everything failed, return empty wide frame
    if not frames or all(f.empty for f in frames):
        return pd.DataFrame(columns=["iso3c", "country", "year"] + list(indicators.keys()))

    # Start from first non-empty frame
    out = None
    for f in frames:
        if not f.empty:
            out = f
            break

    # Merge rest
    for f in frames:
        if f is out or f.empty:
            continue

        # Drop country in later frames to prevent duplicates
        if "country" in f.columns:
            f = f.drop(columns=["country"])

        out = out.merge(f, on=["iso3c", "year"], how="outer")

    return out.sort_values(["iso3c", "year"]).reset_index(drop=True)
