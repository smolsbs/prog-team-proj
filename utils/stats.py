# pyright: basic

import os

import pandas as pd
import numpy as np

STAT_HEADER ="""=== Earthquakes ===
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

CHOICE = {"1": "Magnitudes", "2": "Distancia","3": "Prof"}


def filter_submenu(type: str):
    os.system("cls")
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
        os.system("cls")
        print(STAT_HEADER + "\n" + STAT_MENU)
        usrIn = input("Opção: ").lower()

        match usrIn:
            case "1":
                # TODO: verificar se estamos a tratar de numeros ou strings
                c = filter_submenu("Média")

                if c is not None:
                    retValue = average(df, c)
                    print(f"A média de {c} é {retValue}")
                else:
                    continue

            case "2":
                c = filter_submenu("Variância")

                if c is not None:
                    retValue = variance(df, c)
                    print(f"A variância dos dados de {c} é {retValue}")
                else:
                    continue

            case "3":
                # TODO: verificar se estamos a tratar de numeros ou strings
                c = filter_submenu("Desvio Padrão")

                if c is not None:
                    retValue = std_dev(df, c)
                    print(f"O desvio padrão de {c} é {retValue}")
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
        input("Clica Enter para continuar")


def average(df: pd.DataFrame, filter_by):
    events = df.drop_duplicates(subset="ID", keep='first')
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    return np.average(values)


def variance(df, filter_by):
    events = df.drop_duplicates(subset="ID", keep='first')
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    return np.var(values)


def std_dev(df, filter_by):
    events = df.drop_duplicates(subset="ID", keep='first')
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)
    
    return np.std(values)


def max_v(df, filter_by):
    events = df.drop_duplicates(subset="ID", keep='first')
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)
    
    return np.max(values)


def min_v(df, filter_by):
    events = df.drop_duplicates(subset="ID", keep='first')
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)
    
    return np.min(values)

def moda(df, filter_by):
    events = df.drop_duplicates(subset="ID", keep='first')
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    uniques, count = np.unique(values, return_counts=True)
    uniques_list = list(zip(uniques, count))

    return sorted(uniques_list, reverse=True ,key=lambda x: x[1])[0][0]


def _unpack_mags(arr: np.ndarray):
    newVals = np.empty(0)
    for v in arr:
        for m in v:
            newVals = np.append(newVals, float(m["Magnitude"]))
    return newVals

