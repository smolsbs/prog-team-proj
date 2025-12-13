import os
import sys
from datetime import datetime

import pandas as pd


def filter_by_date(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """Retorna uma nova DataFrame filtrada por datas de inicio e fim

    Args:
        df (pd.DataFrame): DataFrame a filtrar
        start_date (str): data de inicio, em formato ISO
        end_date (str): data de fim, em formato ISO

    Returns:
        pd.DataFrame: DataFrame filtrada
    """
    # FIX: filtragem por datas usando datetime
    mask = (df["Data"] >= start_date) & (df["Data"] <= end_date)
    return df.loc[mask]


def filter_by_depth(
    df: pd.DataFrame, min_depth: float, max_depth: float
) -> pd.DataFrame:
    """Retorna uma nova DataFrame, filtrada entre um intervalo de profundidades

    Args:
        df (pd.DataFrame): DataFrame a filtrar
        min_depth (float): profundidade minima
        max_depth (float): profundidade maxima

    Returns:
        pd.DataFrame: DataFrame filtrada
    """
    mask = (df["Profundidade"] >= min_depth) & (df["Profundidade"] <= max_depth)
    return df.loc[mask]


def filter_by_magnitude(
    df: pd.DataFrame, min_mag: float, max_mag: float, mag_type: str = "L"
) -> pd.DataFrame:
    """Retorna uma nova DataFrame, filtrada entre um intervalo de magnitudes.

    [description]

    Args:
        df (pd.DataFrame): DataFrame a filtrar
        min_mag (float): magnitude minima
        max_mag (float): magnitude maxima
        mag_type (str): Tipo de magnitude a filtrar (default: `'L'`)

    Returns:
        pd.DataFrame: DataFrame filtrada
    """

    def _filter_mag(mags):
        # Filtrar por tipo de magnitude específico
        vals = [float(m["Magnitude"]) for m in mags if m.get("Tipo") == mag_type]
        if not vals:
            return False
        # Se houver múltiplas magnitudes do mesmo tipo, usa o máximo para filtragem
        mx = max(vals)
        return min_mag <= mx <= max_mag

    mask = df["Magnitudes"].apply(_filter_mag)
    return df.loc[mask]


# -- t7 filters


def filter_by_gap(df: pd.DataFrame, max_gap: float) -> pd.DataFrame:
    """Retorna uma nova DataFrame, filtrada por valores do GAP inferiores a `max_gap`

    Args:
        df (pd.DataFrame): DataFrame a filtrar
        max_gap (float): valor GAP maximo

    Returns:
        pd.DataFrame: DataFrame filtrada
    """
    # Filtra onde Gap <= max_gap
    return df[df["Gap"] <= max_gap]


def filter_by_quality(df: pd.DataFrame, quality: str) -> pd.DataFrame:
    """Retorna uma nova DataFrame para eventos apenas com qualidade especificada

    Args:
        df (pd.DataFrame): DataFrame a filtrar
        quality (str): Qualidade a filtrar

    Returns:
        pd.DataFrame: DataFrame filtrada
    """
    return df[df["Pub"] == quality]


def filter_by_zone(df: pd.DataFrame, zone_type: str, zone_val: str) -> pd.DataFrame:
    """Retorna uma nova DataFrame para eventos de uma certa zona

    Args:
        df (pd.DataFrame): DataFrame a filtrar
        zone_type (str): Tipo da zona, (ex: VZ, SZ)
        zone_val (str): Valor da zona

    Returns:
        pd.DataFrame: DataFrame filtrada
    """
    return df[df[zone_type] == zone_val]


FILTER_MENU = """[1] Filtrar por Data (Inicio:Fim)
[2] Filtrar por Gap (< Valor)
[3] Filtrar por Qualidade (EPI)
[4] Filtrar por Zona SZ
[5] Filtrar por Zona VZ
[6] Filtrar por Magnitude (Min:Max)
[7] Filtrar por Profundidade (Min:Max)
[R] Reset Filtros

[Q] Voltar
"""


def filter_menu(db: pd.DataFrame, original_db: pd.DataFrame) -> pd.DataFrame:
    """Menu de filtragem da DataFrame, com base em datas, magnitudes, profundidades, zonas, GAP e qualidades,
    com opcao para reverter para a DataFrame original, para remocao dos filtros aplicados

     Args:
         db (pd.DataFrame): DataFrame a ser filtrada
         original_db (pd.DataFrame): DataFrame de origem, para reversao

     Returns:
         pd.DataFrame: Retorna a DataFrame com os filtros aplicados, ou a original sem qualquer filtro aplicado.
    """
    currDb = db

    while True:
        os.system("cls" if sys.platform == "windows" else "clear")
        print("=== T7: Filtros ===")
        print(f"Linhas actuais: {len(currDb)}")
        print(FILTER_MENU)
        usrIn = input("Opção: ").lower()

        match usrIn:
            case "1":
                start = input("Data Inicio (YYYY-MM-DD): ")
                end = input("Data Fim    (YYYY-MM-DD): ")
                currDb = filter_by_date(currDb, start, end)

            case "2":
                val = float(input("Gap Máximo: "))
                currDb = filter_by_gap(currDb, val)

            case "3":
                confirm = input(
                    "Filtrar apenas eventos com Qualidade EPI? (s/n): "
                ).lower()
                if confirm == "s":
                    currDb = filter_by_quality(currDb, "EPI")
                else:
                    print("Filtro não aplicado.")

            case "4":
                val = input("Zona SZ (ex: SZ31): ")
                currDb = filter_by_zone(currDb, "SZ", val)

            case "5":
                val = input("Zona VZ (ex: VZ14): ")
                currDb = filter_by_zone(currDb, "VZ", val)

            case "6":
                print("Filtrar por Magnitude Tipo 'L'")
                min_m = float(input("Min Mag L: "))
                max_m = float(input("Max Mag L: "))

                currDb = filter_by_magnitude(currDb, min_m, max_m, "L")

            case "7":
                min_d = float(input("Min Profundidade: "))
                max_d = float(input("Max Profundidade: "))
                currDb = filter_by_depth(currDb, min_d, max_d)

            case "r":
                currDb = original_db.copy()

            case "q":
                return currDb
            case _:
                pass
