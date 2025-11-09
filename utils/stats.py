# pyright: basic

import os

import pandas as pd
import numpy as np

STAT_MENU = """=== Earthquakes ===
 == Estatísticas == 
[1] Média
[2] Variância
[3] Desvio padrão
[4] Máximo
[5] Mínimo

[Q] Voltar ao menu principal
"""


def stat_menu(df: pd.DataFrame):
    inStats = True
    while inStats:
        os.system("cls")
        print(STAT_MENU)
        usrIn = input("Opção: ").lower()

        match usrIn:
            case "1":
                pass
            case "2":
                pass
            case "3":
                pass
            case "4":
                pass
            case "5":
                pass
            case "q":
                inStats = False
                pass
            case _:
                pass


def average(df: pd.DataFrame, filter_by):
    values = df[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    return np.average(values)


def variance(df, filter_by):
    values = df[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    return np.var(values)


def std_dev(df, filter_by):
    values = df[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)
    
    return np.std(values)


def max(df, filter_by):
    values = df[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)
    
    return np.max(values)


def min(df, filter_by):
    values = df[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)
    
    return np.min(values)


def _unpack_mags(arr: np.ndarray):
    newVals = np.empty(0)
    for v in arr:
        for m in v:
            newVals = np.append(newVals, np.float32(m["Magnitude"]))
    return newVals

