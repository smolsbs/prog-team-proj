import io
from collections import defaultdict
from datetime import datetime
from typing import Any

import pandas as pd

"""Parser de dados

A dataframe retornada tera multiplas linhas referentes ao mesmo evento
visto que se esta a guardar por linha cada estacao que registou o evento em questa
logo cada linha tem sempre a mesma informacao duplicada que se encontra no preambulo
para cada estacao

"""


# --- variáveis globais ---
DIST_IND = {"L": "Local", "R": "Regional", "D": "Distante"}
TYPE = {"Q": "Quake", "V": "Volcanic", "U": "Unknown", "E": "Explosion"}


# --- funções auxiliares ---
def is_blank(_str: str) -> bool:
    """Verifica se uma string tem ou nao conteudo

    Args:
        _str (str): str a verificar se esta vazia

    Returns:
        bool: True se str tem conteudo, False caso contrario
    """
    return len(_str.strip(" ")) == 0


def parse_flt(value: str) -> float | None:
    """Formata str como float

    Args:
        value (str): nro em string para ser formatado

    Returns:
        float | None: Retorna um float se bem sucedido, None se excepcao
    """
    try:
        return float(value)
    except ValueError:
        return None


def parse_int(value: str) -> int | None:
    """Formata str como int

    Args:
        value (str): nro em string para ser formatado

    Returns:
        int | None: Retorna um int se bem sucedido, None se excepcao
    """
    try:
        return int(value)
    except ValueError:
        return None


def into_dataframe(data: dict[str, Any]) -> pd.DataFrame:
    """Transforma uma dict numa DataFrame

    Args:
        data (dict[str, Any]): [description]

    Returns:
        pd.DataFrame: DataFrame
    """
    if len(data) == 0:
        return pd.DataFrame()
    aux = {k: [] for k in data.keys()}
    for k, v in data.items():
        aux[k].append(v)

    return pd.DataFrame(data=aux)


def _concat(preamble: dict[str, Any], df: pd.DataFrame) -> pd.DataFrame:
    """Junta o preambulo, uma dict, na DataFrame

    Args:
        preamble (dict[str, Any]): Preambulo do evento a inserir
        df (pd.DataFrame): DataFrame com eventos

    Returns:
        [type]: Nova DataFrame com o preambulo adicionado
    """
    for k, v in preamble.items():
        df.insert(len(df.columns) - 1, k, [v for _ in range(len(df))])

    return df


# --- principal ---
def parse(fname: str) -> pd.DataFrame:
    """Faz o parse de todos os eventos no ficheiro.

    A funcao separa em eventos singulares, e transforma cada evento numa DataFrame,
    que sera concatenada com uma DataFrame que contem todos os eventos existentes

    Args:
        fname (str): nome do ficheiro que contem os dados

    Returns:
        pd.DataFrame: DataFrame com os eventos formatados
    """
    fp = open(fname)
    data = [line for line in fp.read().split("\n")]
    chunks = boundaries(data)
    df = pd.DataFrame()
    for c in chunks:
        a = parse_chunk(data[c[0] : c[1]])
        aux = pd.concat([df, a], axis=0, ignore_index=True)
        df = aux
    fp.close()
    return df


def boundaries(data: list[str]) -> list[tuple[int, int]]:
    """Procura e guarda a posicao de cada evento.

    O ficheiro tem os eventos separados por uma linha em branco

    Args:
        data (list[str]): lista dos dados

    Returns:
        list[tuple[int, int]]: lista com tuples dos indices de inicio
            e fim de cada evento
    """
    boundaries = []
    eventStart = None
    for idx, line in enumerate(data):
        if eventStart is None:
            if not is_blank(line):
                eventStart = idx
        else:
            if is_blank(line):
                boundaries.append((eventStart, idx))
                eventStart = None
    return boundaries


def parse_chunk(chunk_lines: list[str]) -> pd.DataFrame:
    """Parse de um evento no formato Nordic, separando num preambulo, e nas estacoes
    Ambos sao enviados para as suas funcoes privadas para serem parsed

    Args:
        chunk_lines (list[str]): lista de str do evento, como slice da lista de todos os eventos

    Returns:
        pd.DataFrame: DataFrame do evento
    """
    separatorIdx = None
    for idx, line in enumerate(chunk_lines):
        if line[-1] == "7":
            separatorIdx = idx
            break
    preambleRet = _parse_preamble(chunk_lines[:separatorIdx])
    phaseRet = _parse_type_7(chunk_lines[separatorIdx:])

    return _concat(preambleRet, phaseRet)


def _parse_preamble(hLines: list[str]) -> dict[str, Any]:
    """Transforma o preambulo numa dict com os valores que precisamos

    Verifica cada linha e separa dentro de uma dict, com a chave sendo o tipo de linha

    Args:
        hLines (list[str]): slice da lista com apenas o preambulo

    Returns:
        dict[str, Any]: dict com os valores necessarios
    """
    lineTypes = defaultdict(list)

    for line in hLines:
        match line[-1]:
            case "1":
                lineTypes[1].append(line)
            case "3":
                lineTypes[3].append(line)
            case "6":
                lineTypes[6].append(line)
            case "E":
                lineTypes["E"].append(line)
            case "I":
                lineTypes["I"].append(line)
            case _:
                pass

    headerDict = dict()
    for k, v in lineTypes.items():
        if len(v) != 0:
            # FUNCS[k] retorna o handle de cada funcao para cada tipo de linha
            headerDict.update(FUNCS[k](v))
    return headerDict


def _parse_type_1(data: list[str]) -> dict[str, Any]:
    """Transforma linhas tipo 1 (data, hora, latitude, longitude, profundidade
    agencia, magnitudes e tipos e nro de estacoes que registaram o evento)

    Args:
        data (list[str]): lista de linhas tipo 1

    Returns:
        dict[str, Any]: dict com os valores necessarios
    """
    y = int(data[0][1:5])
    mo = int(data[0][6:8])
    d = int(data[0][8:10])
    h = int(data[0][11:13])
    m = int(data[0][13:15])
    s = int(data[0][16:18])
    mil = int(data[0][19]) * 10**5
    dt = datetime(y, mo, d, h, m, s, mil)

    dist_ind = DIST_IND[data[0][21]]
    ev_type = TYPE[data[0][22]]
    lat = float(data[0][23:30])
    long = float(data[0][30:38])
    depth = float(data[0][38:43])
    no_stat = int(data[0][48:51])

    hypo = {
        # NOTE: ANTES ERA UMA STRING, AGORA E O OBJECTO DATETIME
        "Data": dt,
        "Distancia": dist_ind,
        "Tipo Evento": ev_type,
        "Latitude": lat,
        "Longitude": long,
        "Profundidade": depth,
        "Estacoes": no_stat,
        "Magnitudes": [],
    }
    for line in data:
        hypo["Magnitudes"] = hypo["Magnitudes"] + _parse_mag(line)

    return hypo


def _parse_mag(line: str) -> list[dict[str, Any]]:
    """Transforma nos varios tipos de magnitudes

    Args:
        line (str): str das linhas tipo 1

    Returns:
        list[dict[str, Any]]: dict com os valores das magnitudes e o seu tipo
    """
    magnitudes = []
    base = 55
    while base < 79:
        m = line[base : base + 4]
        mt = line[base + 4]
        if not is_blank(m):
            magnitudes.append({"Magnitude": m, "Tipo": mt})
        base += 8
    return magnitudes


def _parse_type_3(data: list[str]) -> dict[str, Any]:
    """Transforma linhas tipo 3 (observacoes)

    Args:
        data (list[str]): lista com linhas tipo 3

    Returns:
        dict[str, Any]: dict com valores necessarios
    """
    comments = {}
    for line in data:
        if (
            line.startswith(" SENTIDO")
            or line.startswith(" REGIAO")
            or line.startswith(" PUB")
        ):
            chave, valor = line[:-2].strip().split(": ", maxsplit=1)

            if chave == "REGIAO":
                parts = valor.split(",")
                comments["Regiao"] = parts[0].strip()
                for p in parts[1:]:
                    p = p.strip()
                    if "SZ" in p:
                        comments["SZ"] = p
                    elif "VZ" in p:
                        comments["VZ"] = p
            elif chave == "PUB":
                comments["Pub"] = valor.strip()
            else:
                comments[chave.capitalize()] = valor.split(",")[0]

    return comments


def _parse_type_6(data: list[str]) -> dict[str, list[str]]:
    """Transforma linhas tipo 6 (nome de onda)

    [description]

    Args:
        data (list[str]): lista de linhas tipo 6

    Returns:
        dict[str, list[str]]: lista de nomes dos ficheiros das ondas
    """
    waves = []
    for line in data:
        waves.append(line.strip().split(" ")[0])
    return {"Onda": waves}


def _parse_type_7(data: list[str]) -> pd.DataFrame:
    """Transforma linhas tipo 7 (estacoes)

    Args:
        data (list[str]): linhas tipo 7

    Returns:
        pd.DataFrame: DataFrame com as informacoes de cada estacao
    """
    aux = io.StringIO("\n".join(data))
    dados = pd.read_fwf(
        aux,
        colspecs=[
            (1, 5),
            (6, 8),
            (10, 15),
            (18, 20),
            (20, 22),
            (23, 28),
            (34, 38),
            (71, 75),
        ],
    )
    dados.rename(
        columns={
            "STAT": "Estacao",
            "SP": "Componente",
            "PHASW": "Tipo Onda",
            "HR": "Hora",
            "MM": "Min",
            "SECON": "Seg",
            "AMPL": "Amplitude",
            " DIST": "Distancia Epicentro",
        },
        inplace=True,
    )
    return dados


def _parse_type_e(data: list[str]) -> dict[str, Any]:
    """Transformar linhas tipo E (erros)

    Args:
        data (list[str]): linhas tipo E

    Returns:
        dict[str, Any]: dict com os valores necessarios
    """
    error = {
        "Gap": int(data[0][5:8]),
        "Origin": float(data[0][14:20]),
        "Error_lat": float(data[0][24:30]),
        "Error_long": float(data[0][32:38]),
        "Error_depth": float(data[0][38:43]),
        "Cov_xy": float(data[0][43:55]),
        "Cov_xz": float(data[0][55:67]),
        "Cov_yz": float(data[0][67:79]),
    }
    return error


def _parse_type_i(data: list[str]) -> dict[str, int]:
    """Transforma linhas tipo I(ID do evento)

    Args:
        data (list[str]): linhas tipo I

    Returns:
        dict[str, int]: dict com o valor do ID
    """
    aux = data[0]
    return {"ID": int(aux[60:74])}


FUNCS = {
    1: _parse_type_1,
    3: _parse_type_3,
    6: _parse_type_6,
    "E": _parse_type_e,
    "I": _parse_type_i,
}


# -- Deprecated


def validate_station_numbers(expected: int, stationsDF: pd.DataFrame) -> bool:
    """[summary]

    [description]

    Args:
        expected (int): [description]
        stationsDF (pd.DataFrame): [description]

    Returns:
        bool: [description]
    """
    uniqueStations = stationsDF["Estacao"].nunique()
    return expected == uniqueStations
