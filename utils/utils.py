#! /usr/bin/env python
# pyright: basic

import json
from datetime import time
from math import modf
from typing import Any

import pandas as pd


def extract_mag_depth(df: pd.DataFrame) -> pd.DataFrame:
    """Extrai as magnitudes e profundidades.

    Nas magnitudes, apenas deixa o tipo L

    Args:
        df (pd.DataFrame): Dataframe com eventos

    Returns:
        pd.DataFrame: Dataframe com apenas magnitudes e profundidades
    """
    _df = df.drop_duplicates(subset="ID", keep="first")[
        ["Magnitudes", "Profundidade"]
    ].reset_index(drop=True)
    mags = []

    for _, value in _df.iterrows():
        for mag in value.Magnitudes:
            if mag["Tipo"] == "L":
                mags.append(float(mag["Magnitude"]))
                break
    _df = _df.drop(columns=["Magnitudes"])
    aux = pd.DataFrame.from_dict({"Magnitudes": mags})
    return pd.concat([aux, _df], axis=1)


def save_as_json(df: pd.DataFrame, fname: str, event_cols: list[str]) -> bool:
    """Guarda a dataframe como um ficheiro JSON


    Args:
        df (pd.DataFrame): Dataframe com eventos
        fname (str): nome do ficheiro a guardar
        event_cols (list[str]): lista com os nomes das colunas presentes em `df`

    Returns:
        bool: Sucesso da operacao
    """
    info = _create_dict_struct(df, event_cols)
    with open(fname, "w") as fp:
        json.dump(info, fp, indent=4)

    return True


def _create_dict_struct(df: pd.DataFrame, event_cols) -> dict[str, Any]:
    """Funcao privada para ajuda a guardar como ficheiro JSON

    [description]

    Args:
        df (pd.DataFrame): [description]
        event_cols ([type]): [description]

    Returns:
        dict[str, Any]: [description]
    """
    uniqueIds = df["ID"].unique()

    allEvents = {}

    for id in uniqueIds:
        filteredDf = df.loc[df["ID"] == id]
        first_row = filteredDf.head(1)
        allEvents[int(id)] = _create_event_info(first_row, event_cols)
        allEvents[int(id)].update(create_stations_info_1(filteredDf))

    return allEvents


def _create_event_info(info: pd.DataFrame, cols) -> dict[str, Any]:
    """Funcao privada para criar a estrutura dict pretendida
    no ficheiro JSOn


    Args:
        info (pd.DataFrame): dataframe com eventos
        cols ([type]): lista com nomes das colunas

    Returns:
        dict[str, Any]: dict com o formato pretendido
    """
    informacoes = dict()

    for v in cols:
        if v == "Data":
            informacoes[v] = info.iloc[0][v].isoformat()
        elif v == "Magnitudes":
            informacoes[v] = create_mag_info(info.iloc[0][v])
        elif v in {"Latitude", "Longitude", "Profundidade", "Gap"}:
            informacoes[v] = float(info.iloc[0][v])
        else:
            informacoes[v] = info.iloc[0][v]

    return informacoes


def create_stations_info_1(info: pd.DataFrame) -> dict[str, Any]:
    """Funcao privada para ajuda de formatacao no guardar como JSON

    Args:
        info (pd.DataFrame): dataframe com eventos

    Returns:
        dict[str, Any]: dict com o formato pretendido
    """
    stationsDict = {}
    for idx in range(len(info)):
        aux = info.iloc[idx]

        micro, sec = tuple(map(int, modf(aux["Seg"])))
        hms = time(
            hour=aux["Hora"], minute=aux["Min"], second=sec, microsecond=micro
        ).strftime("%H:%M:%S.%f")
        station = {
            "Componente": aux["Componente"],
            "Hora": hms,
            "Distancia": float(aux["DIS"]),
        }

        if type(aux["Tipo Onda"]) is float:
            station.update({"Tipo Onda": aux["Tipo Onda"]})
            if aux["Tipo Onda"] == "IAML":
                station.update({"Amplitude": float(aux["Amplitude"])})

        if aux["Estacao"] not in stationsDict.keys():
            stationsDict[aux["Estacao"]] = [station]
        else:
            stationsDict[aux["Estacao"]].append(station)
    return {"Estacoes": stationsDict}


def create_mag_info(magnitudes: list[dict[str, Any]]) -> dict[str, Any]:
    """Funcao privada para parsing das magnitudes

    Args:
        magnitudes (list[dict[str, Any]]): [description]

    Returns:
        dict[str, Any]: dict com o formato pretendido
    """
    mags = {}
    for value in magnitudes:
        mags[value["Tipo"]] = value["Magnitude"]
    return mags
