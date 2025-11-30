import requests
import pandas as pd


def fetch_indicator(indicator: str, date: str = "1960:2023") -> pd.DataFrame:
    """
    Fetch a single indicator from the World Bank API.

    Parameters
    ----------
    indicator : str
        World Bank indicator code (e.g., "NY.GDP.PCAP.CD").
    date : str, default="1960:2023"
        Year range to request in "start:end" format.

    Returns
    -------
    pd.DataFrame
        Columns: ['iso3c', 'country', 'year', 'value']
        One row per country-year observation.
    """
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

        if isinstance(payload, dict) and "message" in payload:
            raise ValueError(payload["message"])

        meta, items = payload[0], payload[1]
        if items is None:
            break

        for it in items:
            iso3 = it.get("countryiso3code")
            if iso3 is None:
                continue
            if iso3 == "WLD":
                continue

            rows.append({
                "iso3c": iso3.strip().upper(),
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

    df = df[df["iso3c"].astype(str).str.len() == 3]

    return df


def fetch_many(indicators: dict, date: str = "1960:2023") -> pd.DataFrame:
    """
    Fetch and merge multiple indicators into a single panel dataset.

    Parameters
    ----------
    indicators : dict
        Map of output column name → indicator code.
        Example: {"gdp_pc": "NY.GDP.PCAP.CD", "life_exp": "SP.DYN.LE00.IN"}
    date : str, default="1960:2023"
        Range of years.

    Returns
    -------
    pd.DataFrame
        Sorted panel data with columns:
        ['iso3c', 'country', 'year', <indicator columns>]
    """
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
