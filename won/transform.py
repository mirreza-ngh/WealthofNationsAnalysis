import pandas as pd


def latest_complete(df: pd.DataFrame, min_cols: int = 2) -> pd.DataFrame:
    """
    Select the latest year per country with at least `min_cols` non-null indicators.

    Useful to avoid artificially missing values in correlation or mapping.

    Parameters
    ----------
    df : pd.DataFrame
        Panel data with ['iso3c', 'year', indicator columns].
    min_cols : int, default=2
        Minimum number of non-null indicator values required.

    Returns
    -------
    pd.DataFrame
        One row per country (latest valid year).
    """
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
    """
    Compute Pearson correlation coefficients between available indicators.

    Parameters
    ----------
    df : pd.DataFrame
        Latest or filtered dataset where rows are countries.

    Returns
    -------
    pd.DataFrame
        Square correlation matrix of numeric indicator columns.
    """
    base_cols = {"iso3c", "year"}
    if "country" in df.columns:
        base_cols.add("country")

    cols = [c for c in df.columns if c not in base_cols]
    return df[cols].corr(method="pearson")
