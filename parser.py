from collections import defaultdict
from datetime import datetime

def is_blank(l: str) -> bool:
    return len(l.strip(" ")) == 0



def parse():
    fp = open("dados.txt")
    data = [l for l in fp.read().split("\n")]
    chunks = boundaries(data)

    for c in chunks:
        parse_chunk(data[c[0]:c[1]])

    fp.close()


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
    header = None
    for (idx, l) in enumerate(chunk_lines):
        print(l[-1])
        if l[-1] == " ":
            header = idx-1
            break
    parse_header(chunk_lines[:header])

from pprint import pprint
def parse_header(hLines: list[str]):
    aux = defaultdict(list)

    for line in hLines:
        match line[-1]:
            case "1":
                aux[1].append(line)
            case "2":
                aux[2].append(line)
            case "3":
                aux[3].append(line)
            case "5":
                aux[5].append(line)
            case "6":
                aux[6].append(line)
            case "E":
                aux["E"].append(line)
            case "I":
                aux["I"].append(line)
            case _:
                raise NotImplemented

    headerDict = dict()
    for (k,v) in aux.items():
        if len(v) != 0:
            headerDict.update(FUNCS[k](v))
    pprint(headerDict)


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


def parse_mag(line: str):
    magnitudes = []
    base = 55
    while base < 80:
        m = line[base:base+4]
        mt = line[base+4]
        if is_blank(m):
            break
        magnitudes.append({"M": m, "T": mt})
        base += 8
    return magnitudes

    
def parse_type_2(data: list[str]):
    return {}

def parse_type_3(data: list[str]):
    return {}

def parse_type_5(data: list[str]):
    return {}

def parse_type_6(data: list[str]):
    return {}

def parse_type_e(data: list[str]):
    aux = data[0]
    error = {"Gap": int(aux[5:8]), "Origin": float(aux[14:20]), "Error_lat": float(aux[24:30]), "Error_long": float(aux[32:38]), "Error_depth": float(aux[38:43]), "Cov_xy": float(aux[43:55]), "Cov_xz": float(aux[55:67]), "Cov_yz": float(aux[67:79])}
    return error


def parse_type_f(data: list[str]):
    return {}

def parse_type_i(data: list[str]):
    return {}

FUNCS = {1: parse_type_1, 2: parse_type_2, 3: parse_type_3, 5: parse_type_5, 6: parse_type_6, "E": parse_type_e, "F": parse_type_f, "I": parse_type_i}


parse()
