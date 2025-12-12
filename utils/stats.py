import os
import sys

import pandas as pd
import numpy as np

STAT_HEADER ="""=== Terramotos ===
 == Estatísticas == 
"""

STAT_MENU = """[1] Média
[2] Variância
[3] Desvio padrão
[4] Máximo
[5] Mínimo
[6] Moda
[T] Estatísticas Temporais (T5)

[Q] Voltar ao menu principal
"""

FILTER_CHOICES = """[1] Magnitudes
[2] Distância
[3] Profundidade

"""

CHOICE = {"1": "Magnitudes", "2": "Distancia","3": "Prof"}


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



# -- t5 funcs

def _get_unique_events(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(subset="ID", keep='first')

def convert_to_datetime(df: pd.DataFrame) -> pd.DataFrame:
    # Converte coluna Data para objetos datetime
    df = df.copy()
    df['Data'] = pd.to_datetime(df['Data'], format='mixed')
    return df

def events_per_period(df: pd.DataFrame, period: str):
    # Calcula o número de eventos por dia ('D') ou mês ('M')
    df = convert_to_datetime(df)
    events = _get_unique_events(df)

    if period == 'M':
        period = 'ME'
        
    res = events.set_index('Data').resample(period).size()
    return res.index, res.values

def stats_depth_month(df: pd.DataFrame):
     # Calcula estatísticas de Profundidade por Mês
     df = convert_to_datetime(df)
     events = _get_unique_events(df)
     
     grouped = events.set_index('Data').resample('ME')['Profundidade']
     
     stats_df = pd.DataFrame({
         'Mean': grouped.mean(),
         'Std': grouped.std(),
         'Median': grouped.median(),
         'Q1': grouped.quantile(0.25),
         'Q3': grouped.quantile(0.75),
         'Min': grouped.min(),
         'Max': grouped.max()
     })
     return stats_df

def stats_mag_month(df: pd.DataFrame):
    # Calcula estatísticas de Magnitude por Mês
    df = convert_to_datetime(df)
    events = _get_unique_events(df)
    
    def get_max_mag(mags):
        vals = [float(m['Magnitude']) for m in mags if 'Magnitude' in m]
        return max(vals) if vals else np.nan

    events = events.copy()
    events['MaxMag'] = events['Magnitudes'].apply(get_max_mag)
    
    grouped = events.set_index('Data').resample('ME')['MaxMag']
    
    stats_df = pd.DataFrame({
         'Mean': grouped.mean(),
         'Std': grouped.std(),
         'Median': grouped.median(),
         'Q1': grouped.quantile(0.25),
         'Q3': grouped.quantile(0.75),
         'Min': grouped.min(),
         'Max': grouped.max()
     })
    return stats_df


# -- t5 menu

T5_MENU = """[1] Número de eventos por dia
[2] Número de eventos por mês
[3] Estatísticas Profundidade por mês
[4] Estatísticas Magnitude por mês

[Q] Voltar
"""

def t5_menu(df: pd.DataFrame):
    while True:
        os.system("cls" if sys.platform == "windows" else "clear")
        print(STAT_HEADER + "\n" + " == T5: Estatísticas Temporais ==\n" + T5_MENU)
        usrIn = input("Opção: ").lower()
        
        match usrIn:
            case "1":
                dates, counts = events_per_period(df, 'D')
                print("\nEventos por Dia:")
                print(pd.DataFrame({'Data': dates, 'Contagem': counts}).to_string(index=False))
            
            case "2":
                dates, counts = events_per_period(df, 'M')
                print("\nEventos por Mês:")
                print(pd.DataFrame({'Data': dates, 'Contagem': counts}).to_string(index=False))

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

            case "q":
                inStats = False
                continue

            case _:
                pass
        
        input("Clica `Enter` para continuar")


def average(df: pd.DataFrame, filter_by):
    events = _get_unique_events(df)
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)
    try:
        return np.average(values)
    except:
        return None


def variance(df, filter_by):
    events = _get_unique_events(df)
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)

    try:
        return np.var(values)
    except:
        return None


def std_dev(df, filter_by):
    events = _get_unique_events(df)
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)
    
    try:
        return np.std(values)
    except:
        return None


def max_v(df, filter_by):
    events = _get_unique_events(df)
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)
    
    return np.max(values)


def min_v(df, filter_by):
    events = _get_unique_events(df)
    values = events[filter_by].to_numpy()

    if filter_by == "Magnitudes":
        values = _unpack_mags(values)
    
    return np.min(values)


def moda(df, filter_by):
    events = _get_unique_events(df)
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

