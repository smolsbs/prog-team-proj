#! /usr/bin/env python
# pyright: basic

from datetime import time
import json
from math import modf
from typing import Any

import pandas as pd


def save_as_json(df: pd.DataFrame, fname, event_cols, station_cols) -> bool:
    info = create_dict_struct(df, event_cols, station_cols)
    with open(fname, "w") as fp:
        json.dump(info, fp, indent=4)
    
    return True

# TODO: passar os nomes das colunas, para não haver problemas no futuro, caso se altere os nomes da dataframe
def create_dict_struct(df: pd.DataFrame, event_cols, station_cols) -> dict[str, Any]:
    # get all events by their id
    uniqueIds = df["ID"].unique()

    allEvents = {}

    for id in uniqueIds:
        filteredDf = df.loc[df["ID"] == id]
        first_row = filteredDf.head(1)
        allEvents[int(id)] = create_event_info(first_row, event_cols)
        allEvents[int(id)].update(create_stations_info_1(filteredDf))

    return allEvents


def create_event_info(info: pd.DataFrame, cols) -> dict[str, Any]:
    informacoes = dict()

    for v in cols:
        if v == "Magnitudes":
            informacoes[v] = create_mag_info(info.iloc[0][v])
        elif v in {"Latitude", "Longitude", "Profundidade", "Gap"}:
            informacoes[v] = float(info.iloc[0][v])
        else:
            informacoes[v] = info.iloc[0][v]

    return informacoes


def create_stations_info_1(info: pd.DataFrame) -> dict[str, Any]:
    stationsDict = {}
    for idx in range(len(info)):
        aux = info.iloc[idx]

        micro, sec = tuple(map(int, modf(aux["Seg"])))
        hms = time(hour=aux["Hora"],minute=aux["Min"], second=sec, microsecond=micro).strftime("%H:%M:%S.%f")
        station = {"Componente": aux["Componente"], "Hora": hms, "Distancia": float(aux["DIS"])}

        if type(aux["Tipo Onda"]) != float:
            station.update({"Tipo Onda": aux["Tipo Onda"]})
            if aux["Tipo Onda"] == "IAML":
                station.update({"Amplitude": float(aux["Amplitude"])})


        if aux["Estacao"] not in stationsDict.keys():
            stationsDict[aux["Estacao"]] = [station]
        else:
            stationsDict[aux["Estacao"]].append(station)
    return {"Estacoes": stationsDict}


def create_mag_info(magnitudes):
    mags = {}
    for value in magnitudes:
        mags[value["Tipo"]] = value["Magnitude"]
    return mags


if __name__ == '__main__':
    import parser

    df = parser.parse("dados.txt")
    a = create_dict_struct(df, None, None)
    save_as_json(a)
