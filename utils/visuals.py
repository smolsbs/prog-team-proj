import matplotlib.pyplot as plt
import pandas as pd
import sys
import os
import numpy as np

from utils import stats

# -- helpers

def plot_bar(x, y, xLabel, yLabel, title):
    plt.figure(figsize=(10, 6))
    plt.bar(x, y)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def plot_linear_with_std(x, mean, std, xLabel, yLabel, title):
    plt.figure(figsize=(10, 6))
    plt.errorbar(x, mean, yerr=std, fmt='-o', capsize=5, ecolor='red')
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(title)
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_boxplot(dataList, labels, xLabel, yLabel, title):
    # dataList: lista de arrays/series, um para cada etiqueta
    # labels: lista de etiquetas correspondentes a dataList
    plt.figure(figsize=(10, 6))
    plt.boxplot(dataList, labels=labels)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.title(title)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

# -- t6 logic

def viz_events_per_period(df: pd.DataFrame, period: str, title_suffix: str):
    dates, counts = stats.events_per_period(df, period)
    # Formatar datas para melhor leitura no gráfico
    if period == 'D':
         # dates é um DatetimeIndex
         labels = [d.strftime('%Y-%m-%d') for d in dates]
    else:
         labels = [d.strftime('%Y-%m') for d in dates]
    
    plot_bar(labels, counts, "Data", "Número de Eventos", f"Eventos por {title_suffix}")

def viz_linear_stats(df: pd.DataFrame, target: str):
    # Média +/- Desvio Padrão
    if target == 'Profundidade':
        st = stats.stats_depth_month(df)
        unit = "km"
    else: # Magnitude
        st = stats.stats_mag_month(df)
        unit = "Magn"
    
    labels = [d.strftime('%Y-%m') for d in st.index]
    
    plot_linear_with_std(labels, st['Mean'], st['Std'], "Mês", f"{target} ({unit})", f"Média e Desvio Padrão de {target} por Mês")

def viz_boxplot(df: pd.DataFrame, target: str):
    df = stats.convert_to_datetime(df)
    events = stats._get_unique_events(df)
    
    # Agrupar por mês
    grouped = events.set_index('Data').resample('ME')
    
    data_to_plot = []
    labels = []
    
    for name, group in grouped:
        if target == 'Profundidade':
             vals = group['Profundidade'].dropna().values
        else:
             # Extrair magnitudes máximas
             def get_max_mag(mags):
                vals = [float(m['Magnitude']) for m in mags if 'Magnitude' in m]
                return max(vals) if vals else np.nan
             vals = group['Magnitudes'].apply(get_max_mag).dropna().values
        
        if len(vals) > 0:
            data_to_plot.append(vals)
            labels.append(name.strftime('%Y-%m'))
            
    plot_boxplot(data_to_plot, labels, "Mês", target, f"Boxplot de {target} por Mês")


# --- Menu ---

VISUALS_MENU = """[1] Gráfico Barras: Eventos por Dia
[2] Gráfico Barras: Eventos por Mês
[3] Gráfico Linear: Profundidade (Média +/- DP) por Mês
[4] Gráfico Linear: Magnitude (Média +/- DP) por Mês
[5] Boxplot: Profundidade por Mês
[6] Boxplot: Magnitude por Mês

[Q] Voltar
"""

HEADER = "=== T6: Representação Gráfica ==="

def visual_menu(df: pd.DataFrame):
    while True:
        os.system("cls" if sys.platform == "windows" else "clear")
        print(HEADER + "\n" + VISUALS_MENU)
        usrIn = input("Opção: ").lower()
        
        match usrIn:
            case "1":
                viz_events_per_period(df, 'D', "Dia")
            case "2":
                viz_events_per_period(df, 'M', "Mês")
            case "3":
                viz_linear_stats(df, "Profundidade")
            case "4":
                viz_linear_stats(df, "Magnitude")
            case "5":
                viz_boxplot(df, "Profundidade")
            case "6":
                viz_boxplot(df, "Magnitude")
            case "q":
                return
            case _:
                pass
