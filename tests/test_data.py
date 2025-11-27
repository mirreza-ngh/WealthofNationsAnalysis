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

        if len(payload) < 2 or payload[1] is None:
            break

        meta, items = payload[0], payload[1]

        for it in items:
            if it["country"]["id"] == "WLD":
                continue

            rows.append({
                "iso3c": it["country"]["id"],
                "country": it["country"]["value"],  # full country name
                "year": int(it["date"]),
                "value": it["value"],
            })

        if page >= meta["pages"]:
            break
        page += 1

    df = pd.DataFrame(rows)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # clean iso3 codes, keep only real countries
    df["iso3c"] = df["iso3c"].astype(str).str.strip().str.upper()
    df = df[df["iso3c"].str.len() == 3]

    return df


def fetch_many(indicators: dict, date: str = "1960:2023") -> pd.DataFrame:
    """Merge multiple indicators wide by (iso3c, country, year)."""
    frames = []
    for col, code in indicators.items():
        dfi = fetch_indicator(code, date).rename(columns={"value": col})
        frames.append(dfi)

    out = frames[0]

    for dfi in frames[1:]:
        out = out.merge(
            dfi,
            on=["iso3c", "year"],
            how="outer",
            suffixes=("_x", "_y")
        )

        # merge country names if duplicates appear
        if "country_x" in out.columns and "country_y" in out.columns:
            out["country"] = out["country_x"].fillna(out["country_y"])
            out = out.drop(columns=["country_x", "country_y"])

    # reorder columns nicely
    cols = ["iso3c", "country", "year"] + [
        c for c in out.columns if c not in ("iso3c", "country", "year")
    ]
    out = out[cols]

    out = out.loc[:, ~out.columns.duplicated()]

    return out.sort_values(["iso3c", "year"]).reset_index(drop=True)
