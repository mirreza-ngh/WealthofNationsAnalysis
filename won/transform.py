import pandas as pd


def latest_complete(df: pd.DataFrame, min_cols: int = 2) -> pd.DataFrame:
    """Latest row per country with at least `min_cols` non-null indicators."""
    base_cols = {"iso3c", "year"}
    if "country" in df.columns:
        base_cols.add("country")

    ind_cols = [c for c in df.columns if c not in base_cols]

    df2 = df.copy()
    df2["non_null"] = df2[ind_cols].notna().sum(axis=1)
    df2 = df2[df2["non_null"] >= min_cols]

    if df2.empty:
        return df2.drop(columns=["non_null"], errors="ignore")

    idx = df2.groupby("iso3c")["year"].idxmax()
    keep_cols = ["iso3c", "year"] + (["country"] if "country" in df.columns else []) + ind_cols

    return (
        df2.loc[idx, keep_cols]
        .sort_values("iso3c")
        .reset_index(drop=True)
    )


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Pearson correlation among indicator columns."""
    base_cols = {"iso3c", "year"}
    if "country" in df.columns:
        base_cols.add("country")

    cols = [c for c in df.columns if c not in base_cols]
    return df[cols].corr(method="pearson")
