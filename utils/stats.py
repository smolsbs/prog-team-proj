import os
import sys
from typing import Any, Iterable

import numpy as np
import pandas as pd

from utils.utils import extract_mag_depth

STAT_HEADER = """=== Terramotos ===
 == Estatísticas ==
"""

STAT_MENU = """[1] Média
[2] Variância
[3] Desvio padrão
[4] Máximo
[5] Mínimo
[6] Moda
[7] Print de todas as estatísticas
[T] Estatísticas Temporais (T5)

[Q] Voltar ao menu principal
"""

FILTER_CHOICES = """[1] Magnitudes
[2] Distância
[3] Profundidade

"""

CHOICE = {"1": "Magnitudes", "2": "Distancia", "3": "Profundidade"}


def filter_submenu(type: str):
    """[summary]

    [description]

    Args:
        type (str): [description]

    Returns:
        [type]: [description]
    """
    os.system("cls" if sys.platform == "windows" else "clear")
    print(f"{STAT_HEADER}\n  = {type} =  ")
    print(FILTER_CHOICES)

    choice = input("Qual dos valores: ")

    try:
        usrChoice = CHOICE[choice]
        return usrChoice
    except KeyError:
        return None


# -- t5 funcs


def _get_unique_events(df: pd.DataFrame) -> pd.DataFrame:
    """Função privada que retorna os eventos únicos

    (Ler docstring do `parser.py` para o porquê de se fazer isto)

    Args:
        df (pd.DataFrame): Dataframe com todos os eventos

    Returns:
        pd.DataFrame: Dataframe com apenas uma linha por evento
    """
    return df.drop_duplicates(subset="ID", keep="first")


def events_per_period(df: pd.DataFrame, period: str) -> tuple[Iterable, Iterable]:
    """Retorna os eventos por período, seja por dia, seja por mês

    Args:
        df (pd.DataFrame): Dataframe com valores
        period (str): tipo de período. `D` para dia, `M` para mês

    Returns:
        tuple[Iterable, Iterable]: tuple com iteradores dos indices e valores
    """
    # Calcula o número de eventos por dia ('D') ou mês ('M')
    events = _get_unique_events(df)

    if period == "M":
        period = "ME"

    res = events.set_index("Data").resample(period).size()
    return (res.index, res.values)


def stats_depth_month(df: pd.DataFrame) -> pd.DataFrame:
    """Estatisticas de profundidade de sismos, por mes

    Args:
        df (pd.DataFrame): DataFrame com eventos

    Returns:
        [type]: Dataframe com as estatisticas de profundidade, por mes
    """
    events = _get_unique_events(df)

    grouped = events.set_index("Data").resample("ME")["Profundidade"]

    stats_df = pd.DataFrame(
        {
            "Mean": grouped.mean(),
            "Std": grouped.std(),
            "Median": grouped.median(),
            "Q1": grouped.quantile(0.25),
            "Q3": grouped.quantile(0.75),
            "Min": grouped.min(),
            "Max": grouped.max(),
        }
    )
    return stats_df


def stats_mag_month(df: pd.DataFrame):
    """Estatisticas de magnitude dos sismos, por mes

    Args:
        df (pd.DataFrame): DataFrame com eventos

    Returns:
        [type]: Dataframe com as estatisticas de magnitude, por mes
    """
    # Calcula estatísticas de Magnitude por Mês
    events = _get_unique_events(df)

    def _get_max_mag(mags: pd.Series):
        """Funcao aplicadora à df, para encontrar a maior magnitude

        Args:
            mags (pd.Series): Serie com as magnitudes

        Returns:
            pd.Series: Serie com a magnitude maxima
        """
        vals = [float(m["Magnitude"]) for m in mags if "Magnitude" in m]
        return max(vals) if vals else np.nan

    events = events.copy()
    events["MaxMag"] = events["Magnitudes"].apply(_get_max_mag)

    grouped = events.set_index("Data").resample("ME")["MaxMag"]

    stats_df = pd.DataFrame(
        {
            "Mean": grouped.mean(),
            "Std": grouped.std(),
            "Median": grouped.median(),
            "Q1": grouped.quantile(0.25),
            "Q3": grouped.quantile(0.75),
            "Min": grouped.min(),
            "Max": grouped.max(),
        }
    )
    return stats_df


# -- t5 menu

T5_MENU = """[1] Número de eventos por dia
[2] Número de eventos por mês
[3] Estatísticas Profundidade por mês
[4] Estatísticas Magnitude por mês

[Q] Voltar
"""


def t5_menu(df: pd.DataFrame):
    """Menu de estatisticas das magnitudes e profundidades por mes

    Args:
        df (pd.DataFrame): Dataframe com os eventos
    """
    while True:
        os.system("cls" if sys.platform == "windows" else "clear")
        print(STAT_HEADER + "\n" + " == T5: Estatísticas Temporais ==\n" + T5_MENU)
        usrIn = input("Opção: ").lower()

        match usrIn:
            case "1":
                dates, counts = events_per_period(df, "D")
                print("\nEventos por Dia:")
                print(
                    pd.DataFrame({"Data": dates, "Contagem": counts}).to_string(
                        index=False
                    )
                )

            case "2":
                dates, counts = events_per_period(df, "M")
                print("\nEventos por Mês:")
                print(
                    pd.DataFrame({"Data": dates, "Contagem": counts}).to_string(
                        index=False
                    )
                )

            case "3":
                st = stats_depth_month(df)
                print("\nEstatísticas Profundidade por Mês:")
                print(st.to_string())

            case "4":
                st = stats_mag_month(df)
                print("\nEstatísticas Magnitude por Mês:")
                print(st.to_string())

            case "q":
                return
            case _:
                pass

        input("\n[Enter] para continuar...")


# -- stat menu


def stat_menu(df: pd.DataFrame):
    """Menu de estatísticas


    Args:
        df (pd.DataFrame): Dataframe com eventos
    """
    inStats = True
    while inStats:
        os.system("cls" if sys.platform == "windows" else "clear")
        print(STAT_HEADER + "\n" + STAT_MENU)
        usrIn = input("Opção: ").lower()

        match usrIn:
            case "t":
                t5_menu(df)
                continue

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
                c = filter_submenu("Moda")

                if c is not None:
                    retValue = moda(df, c)
                    print(f"O valor moda em {c} é {retValue}")
                else:
                    continue

            case "7":
                m, d = _mag_depth(df)

                print("\t\tMagnitude\tProfundidade")
                for a, b in zip(m, d):
                    print(f"{a[0]}\t{round(a[1], 4)}\t\t{round(b[1], 4)}")

            case "q":
                inStats = False
                continue

            case _:
                pass

        input("Clica `Enter` para continuar")


type tuples = tuple[list[tuple[str, Any]], list[tuple[str, Any]]]


def _mag_depth(df: pd.DataFrame) -> tuples:
    """Cria uma lista com cada estatística para as magnitudes e profundidades,
    de forma a ser possivel fazer print de tudo de uma só vez


    Args:
        df (pd.DataFrame): Dataframe com valores

    Returns:
        tuples: lista com estatisticas das magnitudes e profundidades
    """
    data = extract_mag_depth(df)

    mag_array = data.Magnitudes.values
    depth_array = data.Profundidade.values

    mags = []
    dep = []
    for a, b in zip(
        ["Media\t", "Desvio-Padrao", "Variancia", "Valor Maximo", "Valor Minimo"],
        [np.average, np.std, np.var, np.max, np.min],
    ):
        mags.append((a, b(mag_array)))
        dep.append((a, b(depth_array)))

    return (mags, dep)


def average(df: pd.DataFrame, filter_by) -> np.float64 | None:
    """Calculo da média para o tipo especifico

    Args:
        df (pd.DataFrame): Dataframe com valores
        filter_by (str): Valor para calculo da media

    Returns:
        np.float64 | None: média
    """
    events = _get_unique_events(df)
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)
    try:
        return np.average(values)
    except Exception:
        return None


def variance(df: pd.DataFrame, filter_by: str) -> np.float64 | None:
    """calcula a variancia para o tipo especificado

    Args:
        df (pd.DataFrame): Dataframe com valores
        filter_by (str): Valor para calculo da variancia

    Returns:
        np.float64 | None: variancia
    """
    events = _get_unique_events(df)
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    try:
        return np.var(values)
    except Exception:
        return None


def std_dev(df: pd.DataFrame, filter_by: str) -> np.float64 | None:
    """calcula o desvio-padrao para o tipo especificado

    Args:
        df (pd.DataFrame): Dataframe com valores
        filter_by (str): Valor para calculo do desvio-padrao

    Returns:
        np.float64 | None: desvio-padrao
    """
    events = _get_unique_events(df)
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    try:
        return np.std(values)
    except Exception:
        return None


def max_v(df: pd.DataFrame, filter_by: str) -> np.floating:
    """Retorna o valor maximo num array

    Args:
        df (pd.DataFrame): Dataframe com valores
        filter_by (str): Coluna para o valor maximo

    Returns:
        np.floating: valor maximo
    """
    events = _get_unique_events(df)
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    return np.max(values)


def min_v(df, filter_by) -> np.floating:
    """Retorna o valor minimo num array

    Args:
        df (pd.DataFrame): Dataframe com valores
        filter_by (str): Coluna para o valor minimo

    Returns:
        np.floating: valor minimo
    """
    events = _get_unique_events(df)
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    return np.min(values)


def moda(df, filter_by) -> np.floating:
    """Calcula a moda para um array de valores


    Args:
        df (pd.DataFrame): Dataframe com valores
        filter_by (str): Coluna para o calculo da moda

    Returns:
        np.floating: moda
    """
    events = _get_unique_events(df)
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    uniques, count = np.unique(values, return_counts=True)
    uniques_list = list(zip(uniques, count))

    return sorted(uniques_list, reverse=True, key=lambda x: x[1])[0][0]


def _unpack_mags(arr: np.ndarray) -> np.ndarray:
    """Funcao privada para facilitar o calculo das magnitudes


    Args:
        arr (np.ndarray): Lista dos tipos de magnitudes

    Returns:
        np.ndarray: magnitudes
    """
    newVals = np.empty(0)
    for v in arr:
        for m in v:
            newVals = np.append(newVals, float(m["Magnitude"]))
    return newVals
