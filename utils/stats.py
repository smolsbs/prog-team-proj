# pyright: basic

import datetime

import numpy as np
import pandas as pd
import utils


def stats(df: pd.DataFrame) -> None:
    """Estatisticas para a DataFrame
    :param df: DataFrame em questão"""

    mags = mags_avg_std(df)
    depth = depth_avg_std(df)

    median_mags = median_mags(df)


def mags_avg_std(data: pd.DataFrame) -> tuple[np.floating, np.floating]:
    """Media e desvio-padrao das magnitudes
    :param data: Dataframe com dados a filtrar
    :returns: Tuple com a media e desvio-padrao
    """
    filtered_data: pd.DataFrame = filter_mags(data)
    vals = filtered_data["MagL"].to_numpy()
    return (np.average(vals), np.std(vals))


def depth_avg_std(data: pd.DataFrame) -> tuple[np.floating, np.floating]:
    """Media e desvio-padrao das profundidades
    :param data: Dataframe com dados a filtrar
    :returns: Tuple com a media e desvio-padrao
    """
    filtered_data: pd.DataFrame = filter_depth(data)
    vals = np.average(filtered_data["Profundidade"].to_numpy())
    return (np.average(vals), np.std(vals))


def median_mags(data: pd.DataFrame):
    filtered_data: pd.DataFrame = filter_mags(data)
    vals = sorted(filtered_data["MagL"].to_numpy())

    quartil = len(vals) // 4

    return (
        filtered_data[quartil, :]["MagL"],
        filtered_data[quartil * 2, :]["MagL"],
        filtered_data[quartil * 3, :]["MagL"],
    )


def filter_mags(data, more_than=None, less_than=None) -> pd.DataFrame:
    """Filters by magnitudes a DataFrame into a new Dataframe

    :param data: Raw pandas DataFrame
    :param more_than(optional): Filter for magnitudes above threshold
    :param after(optional): Filters for dates after set date
    :returns: Returns a filtered pandas DataFrame
    """
    v = data.drop_duplicates(subset="ID", keep="first")
    _dict = {"Data": [], "MagL": []}
    for idx, c in v.iterrows():
        _dict["Data"].append(str(c.Data))
        _dict["MagL"].append(utils.extract_mag_l(c.Magnitudes))

    _df = pd.DataFrame.from_dict(_dict)
    if more_than:
        _df = _df[_df["MagL"] >= more_than]

    if less_than:
        _df = _df[_df["MagL"] <= less_than]
    return _df


def filter_date(
    data: pd.DataFrame,
    before: datetime.datetime | None = None,
    after: datetime.datetime | None = None,
) -> pd.DataFrame:
    """Filters by date a DataFrame into a new Dataframe

    :param data: Raw pandas DataFrame
    :param before(optional): Filter for dates before set date
    :param after(optional): Filters for dates after set date
    :returns: Returns a filtered pandas DataFrame
    """
    v = data
    for idx, c in v.iterrows():
        v.at[idx, "Data"] = datetime.datetime.fromisoformat(c.Data)

    if after:
        v = v[v["Data"] >= after]

    if before:
        v = v[v["Data"] >= before]
    return v


def filter_depth(
    data: pd.DataFrame,
    less_than: float | None = None,
    more_than: float | None = None,
) -> pd.DataFrame:
    """Filters by the depth a DataFrame into a new Dataframe

    :param data: Raw pandas DataFrame
    :param less_than(optional): Filter for depths below the threshold
    :param after(optional): Filters for depths deeper than threshold
    :returns: Returns a filtered pandas DataFrame
    """
    v = data.drop_duplicates(subset="ID", keep="first")

    if more_than:
        v = v[v["Profundidade"] >= more_than]

    if less_than:
        v = v[v["Profundidade"] >= less_than]
    return v


def filter_gap(
    data: pd.DataFrame,
    threshold: int,
) -> pd.DataFrame:
    """Filters by the depth a DataFrame into a new Dataframe

    :param data: Raw pandas DataFrame
    :param threshold: Filter for GAPS below the threshold
    :returns: Returns a filtered pandas DataFrame
    """
    v = data.drop_duplicates(subset="ID", keep="first")
    v = v[v["Gap"] <= threshold]
    return v


def filter_sz(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Filters by SZ plane a DataFrame into a new Dataframe

    :param data: Raw pandas DataFrame
    :returns: Returns a filtered pandas DataFrame
    """
    v = data[data["SZ"].notna()]
    return v


def filter_vz(
    data: pd.DataFrame,
) -> pd.DataFrame:
    """Filters by VZ plane a DataFrame into a new Dataframe

    :param data: Raw pandas DataFrame
    :returns: Returns a filtered pandas DataFrame
    """
    v = data[data["VZ"].notna()]
    return v


def _preprare_days(data):
    c = data.Data.to_list()
    for idx, d in enumerate(c):
        aux = datetime.datetime.fromisoformat(d)
        c[idx] = datetime.datetime.strftime(aux, "%Y-%m-%d")

    return c


def _preprare_months(data):
    c = data.Data.to_list()
    for idx, d in enumerate(c):
        aux = datetime.datetime.fromisoformat(d)
        c[idx] = datetime.datetime.strftime(aux, "%Y-%m")

    return c
