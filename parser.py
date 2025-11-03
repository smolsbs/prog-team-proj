import io
import warnings

from collections import defaultdict
from datetime import datetime

import pandas as pd

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


def test(d1, d2):
    for col in d2.columns:
        d1.at[0, col] = d2[col].tolist()
    return d1

# ------------ principal

def parse(fname="dados.txt"):
    fp = open(fname)
    data = [l for l in fp.read().split("\n")]
    chunks = boundaries(data)
    df = pd.DataFrame()
    for (idx,c) in enumerate(chunks):
        a = parse_chunk(data[c[0]:c[1]], idx)
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


def parse_chunk(chunk_lines: list[str], iD):
    hIdx = None
    for (idx, l) in enumerate(chunk_lines):
        if l[-1] == "7":
            hIdx = idx
            break
    headersRet = parse_header(chunk_lines[:hIdx])
    phaseRet = parse_type_7(chunk_lines[hIdx:])

    hDF = into_dataframe(headersRet)
    hDF["ID"] = iD
    phaseRet["ID"] = iD

    return pd.concat([hDF, phaseRet])
    

def parse_header(hLines: list[str]):
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
                aux["E"].append(line)
            case "I":
                aux["I"].append(line)
            case "F":
                aux["F"].append(line)
            case unknown:
                warnings.warn(f"header type not implemented: {unknown}")

    headerDict = dict()
    for (k,v) in aux.items():
        if len(v) != 0:
            headerDict.update(FUNCS[k](v))
    return headerDict


def parse_mag(line: str):
    magnitudes = []
    base = 55
    while base < 79:
        m = line[base:base+4]
        mt = line[base+4]
        if not is_blank(m):
            magnitudes.append({"M": m, "T": mt})
        base += 8
    return magnitudes


def parse_type_1(data: list[str]):
    aux = data[0]
    y = int(aux[1:5])
    mo = int(aux[6:8])
    d = int(aux[8:10])
    h = int(aux[11:13])
    m = int(aux[13:15])
    s = int(aux[16:18])
    mil = int(aux[19]) * 10**5
    dt = datetime(y,mo,d,h,m,s,mil)

    dist_ind = aux[21]
    eId = aux[22]
    lat = float(aux[23:30])
    long = float(aux[30:38])
    depth = float(aux[38:43])
    rep_ag = aux[45:48]

    hypo = {"DateTime": dt.isoformat(), "Distance Indicator": dist_ind, "Event ID": eId, "Lat": lat, "Long": long, "Depth": depth, "Agency": rep_ag, "Magnitudes": list()}
    for l in data:
        hypo["Magnitudes"] = hypo["Magnitudes"] + parse_mag(l)

    return hypo

def parse_type_3(data: list[str]):
    comments = []
    for line in data:
        comments.append(line[:-2].strip())
    return {"Comments": comments}


def parse_type_6(data: list[str]):
    waves = []
    for l in data:
        waves.append(l.strip().split(" ")[0])
    return {"Wave": waves}

def parse_type_7(data: list[str]):
    aux = io.StringIO("\n".join(data))
    dados = pd.read_fwf(aux, colspecs=[(1,5), (6,8), (9,10), (10,15), (16,17), (18,22), (23,28), (29,33), (34,40), (41,45), (46,50), (51,56), (57,60), (61,63), (64,68), (69,70), (72,75), (76,79)])
    return dados



def parse_type_e(data: list[str]):
    aux = data[0]
    error = {"Gap": int(aux[5:8]), "Origin": float(aux[14:20]), "Error_lat": float(aux[24:30]), "Error_long": float(aux[32:38]), "Error_depth": float(aux[38:43]), "Cov_xy": float(aux[43:55]), "Cov_xz": float(aux[55:67]), "Cov_yz": float(aux[67:79])}
    return error


def parse_type_f(data: list[str]):
    return {}


def parse_type_i(data: list[str]):
    aux = data[0]
    dt = datetime.strptime(aux[12:26], "%y-%m-%d %H:%M")
    return {"Action": aux[8:11], "Action Extra": {"Date": dt.isoformat(), "OP": aux[30:35].strip(), "Status": aux[42:57].strip(), "ID":int(aux[60:74])}}


FUNCS = {1: parse_type_1, 3: parse_type_3, 6: parse_type_6, "E": parse_type_e, "F": parse_type_f, "I": parse_type_i}

parse()
