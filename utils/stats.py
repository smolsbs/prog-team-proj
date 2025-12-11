# pyright: basic

import datetime
import os
import sys

import numpy as np
import pandas as pd
import utils

STAT_HEADER = """=== Terramotos ===
 == Estatísticas ==
"""

STAT_MENU = """[1] Média
[2] Variância
[3] Desvio padrão
[4] Máximo
[5] Mínimo
[6] Moda

[Q] Voltar ao menu principal
"""

FILTER_CHOICES = """[1] Magnitudes
[2] Distância
[3] Profundidade

"""

CHOICE = {"1": "Magnitudes", "2": "Distancia", "3": "Prof"}


def filter_submenu(type: str):
    os.system("cls" if sys.platform == "windows" else "clear")
    print(f"{STAT_HEADER}\n  = {type} =  ")
    print(FILTER_CHOICES)

    choice = input("Qual dos valores: ")

    try:
        usrChoice = CHOICE[choice]
        return usrChoice
    except KeyError:
        return None


def stat_menu(df: pd.DataFrame):
    inStats = True
    while inStats:
        os.system("cls" if sys.platform == "windows" else "clear")
        print(STAT_HEADER + "\n" + STAT_MENU)
        usrIn = input("Opção: ").lower()

        match usrIn:
            case "1":
                c = filter_submenu("Média")

                if c is not None:
                    retValue = average(df, c)
                    if retValue:
                        print(f"A média de {c} é {retValue}")
                    else:
                        print("Um erro aconteceu. Nada a apresentar de momento.")
                else:
                    continue

            case "2":
                c = filter_submenu("Variância")

                if c is not None:
                    retValue = variance(df, c)
                    if retValue:
                        print(f"A variância dos dados de {c} é {retValue}")
                    else:
                        print("Um erro aconteceu. Nada a apresentar de momento.")
                else:
                    continue

            case "3":
                c = filter_submenu("Desvio Padrão")

                if c is not None:
                    retValue = std_dev(df, c)
                    if retValue:
                        print(f"O desvio padrão de {c} é {retValue}")
                    else:
                        print("Um erro aconteceu. Nada a apresentar de momento.")
                else:
                    continue

            case "4":
                c = filter_submenu("Máximo")

                if c is not None:
                    retValue = max_v(df, c)
                    print(f"O valor máximo em {c} é {retValue}")
                else:
                    continue

            case "5":
                c = filter_submenu("Mínimo")

                if c is not None:
                    retValue = min_v(df, c)
                    print(f"O valor mínimo em {c} é {retValue}")
                else:
                    continue

            case "6":
                c = filter_submenu("Mínimo")

                if c is not None:
                    retValue = moda(df, c)
                    print(f"O valor moda em {c} é {retValue}")
                else:
                    continue

            case "q":
                inStats = False
                continue

            case _:
                pass
        input("Clica `Enter` para continuar")


def average(df: pd.DataFrame, filter_by):
    events = df.drop_duplicates(subset="ID", keep="first")
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)
    try:
        return np.average(values)
    except:
        return None


def variance(df, filter_by):
    events = df.drop_duplicates(subset="ID", keep="first")
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    try:
        return np.var(values)
    except:
        return None


def std_dev(df, filter_by):
    events = df.drop_duplicates(subset="ID", keep="first")
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    try:
        return np.std(values)
    except:
        return None


def max_v(df, filter_by):
    events = df.drop_duplicates(subset="ID", keep="first")
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    return np.max(values)


def min_v(df, filter_by):
    events = df.drop_duplicates(subset="ID", keep="first")
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    return np.min(values)


def moda(df, filter_by):
    events = df.drop_duplicates(subset="ID", keep="first")
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    uniques, count = np.unique(values, return_counts=True)
    uniques_list = list(zip(uniques, count))

    return sorted(uniques_list, reverse=True, key=lambda x: x[1])[0][0]


def _unpack_mags(arr: np.ndarray):
    newVals = np.empty(0)
    for v in arr:
        for m in v:
            newVals = np.append(newVals, float(m["Magnitude"]))
    return newVals


def filter_mags(data, more_than=None, less_than=None):
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
