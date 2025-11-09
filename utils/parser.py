# pyright: basic
import io

from collections import defaultdict
from datetime import datetime

import pandas as pd

# --- globals ---
DIST_IND = {"L": "Local", "R": "Regional", "D": "Distante"}
TYPE = {"Q": "Quake", "V": "Volcanic", "U": "Unknown", "E": "Explosion"}


# --- helper funcs --- 
def is_blank(l: str) -> bool:
    return len(l.strip(" ")) == 0

def parse_flt(v:str) -> float | None:
    try:
        t = float(v)
        return t
    except ValueError:
        return None

def parse_int(v:str) -> int | None:
    try:
        t = int(v)
        return t
    except ValueError:
        return None

def into_dataframe(data) -> pd.DataFrame:
    if len(data) == 0:
        return pd.DataFrame()
    aux = {k: [] for k in data.keys()}
    for (k,v) in data.items():
        aux[k].append(v)

    return pd.DataFrame(data=aux)

def _concat(preamble, df: pd.DataFrame):
    for (k,v) in preamble.items():
        df.insert(len(df.columns)-1, k, [v for _ in range(len(df))])

    return df

def validate_no_stations(expected:int , stationsDF:pd.DataFrame) -> bool:
    uniqueStations = stationsDF["Estacao"].nunique()
    return expected == uniqueStations


# --- principal ---
def parse(fname):
    fp = open(fname)
    data = [l for l in fp.read().split("\n")]
    chunks = boundaries(data)
    df = pd.DataFrame()
    for (idx,c) in enumerate(chunks):
        a = parse_chunk(data[c[0]:c[1]])
        aux = pd.concat([df, a], axis=0, ignore_index=True)
        df = aux
    fp.close()
    return df

def boundaries(data: list[str]):
    boundaries = []
    start = None
    for (idx,l) in enumerate(data):
        if start is None:
            if not is_blank(l):
                start = idx
        else:
            if is_blank(l):
                boundaries.append((start,idx))
                start = None
    return boundaries

def parse_chunk(chunk_lines: list[str]):
    hIdx = None
    for (idx, l) in enumerate(chunk_lines):
        if l[-1] == "7":
            hIdx = idx
            break
    preambleRet = _parse_preamble(chunk_lines[:hIdx])
    phaseRet = _parse_type_7(chunk_lines[hIdx:])

    if not validate_no_stations(preambleRet["Estacoes"], phaseRet):
        pass

    return _concat(preambleRet, phaseRet)

def _parse_preamble(hLines: list[str]):
    aux = defaultdict(list)

    for line in hLines:
        match line[-1]:
            case "1":
                aux[1].append(line)
            case "3":
                aux[3].append(line)
            case "6":
                aux[6].append(line)
            case "E":
                pass
                # aux["E"].append(line)
            case "I":
                aux["I"].append(line)
            case "F":
                pass
                # aux["F"].append(line)
            case _:
                pass

    headerDict = dict()
    for (k,v) in aux.items():
        if len(v) != 0:
            headerDict.update(FUNCS[k](v))
    return headerDict


def _parse_type_1(data: list[str]):
    aux = data[0]
    y = int(aux[1:5])
    mo = int(aux[6:8])
    d = int(aux[8:10])
    h = int(aux[11:13])
    m = int(aux[13:15])
    s = int(aux[16:18])
    mil = int(aux[19]) * 10**5
    dt = datetime(y,mo,d,h,m,s,mil)

    dist_ind = DIST_IND[aux[21]]
    ev_type = TYPE[aux[22]]
    lat = float(aux[23:30])
    long = float(aux[30:38])
    depth = float(aux[38:43])
    no_stat = int(aux[48:51])

    hypo = {"Data": dt.isoformat(), "Distancia": dist_ind, "Tipo Ev": ev_type, "Lat": lat, "Long": long, "Prof": depth, "Estacoes": no_stat, "Magnitudes": list()}
    for l in data:
        hypo["Magnitudes"] = hypo["Magnitudes"] + _parse_mag(l)

    return hypo

def _parse_mag(line: str):
    magnitudes = []
    base = 55
    while base < 79:
        m = line[base:base+4]
        mt = line[base+4]
        if not is_blank(m):
            magnitudes.append({"Magnitude": m, "Tipo": mt})
        base += 8
    return magnitudes


def _parse_type_3(data: list[str]):
    comments = {}
    for line in data:
        if line.startswith(" SENTIDO") or line.startswith(" REGIAO"):
            c, v = line[:-2].strip().split(": ", maxsplit=1)
            comments[c.capitalize()] = v

    return comments


def _parse_type_6(data: list[str]):
    waves = []
    for l in data:
        waves.append(l.strip().split(" ")[0])
    return {"Onda": waves}


def _parse_type_7(data: list[str]):
    aux = io.StringIO("\n".join(data))
    dados = pd.read_fwf(aux, colspecs=[(1,5), (6,8),(10,15), (18,20), (20,22), (23,28), (34,38)])
    dados.rename(columns={'STAT': "Estacao", 'SP': "Componente" , 'PHASW': "Tipo Onda", 'HR': "Hora", 'MM': "Min", 'SECON': "Seg", 'AMPL': "Amplitude"}, inplace=True)
    return dados


def _parse_type_e(data: list[str]):
    aux = data[0]
    error = {"Gap": int(aux[5:8]), "Origin": float(aux[14:20]), "Error_lat": float(aux[24:30]), "Error_long": float(aux[32:38]), "Error_depth": float(aux[38:43]), "Cov_xy": float(aux[43:55]), "Cov_xz": float(aux[55:67]), "Cov_yz": float(aux[67:79])}
    return error


def _parse_type_i(data: list[str]):
    aux = data[0]
    return {"ID":int(aux[60:74])}


FUNCS = {1: _parse_type_1, 3: _parse_type_3, 6: _parse_type_6, "E": _parse_type_e, "I": _parse_type_i}

parse("dados.txt")
