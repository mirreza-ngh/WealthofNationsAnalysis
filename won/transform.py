import pandas as pd

def latest_complete(df: pd.DataFrame, min_cols: int = 2) -> pd.DataFrame:
    """Latest row per country with at least `min_cols` non-null indicators."""
    ind_cols = [c for c in df.columns if c not in ("iso3c", "year")]
    df2 = df.copy()
    df2["non_null"] = df2[ind_cols].notna().sum(axis=1)
    df2 = df2[df2["non_null"] >= min_cols]
    idx = df2.groupby("iso3c")["year"].idxmax()
    return df2.loc[idx, ["iso3c", "year"] + ind_cols].sort_values("iso3c").reset_index(drop=True)

def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Pearson correlation among indicator columns."""
    cols = [c for c in df.columns if c not in ("iso3c", "year")]
    return df[cols].corr(method="pearson")
