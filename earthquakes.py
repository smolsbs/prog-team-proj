#! /usr/bin/env python
# pyright: basic

import json
import os
import sys
from datetime import datetime
from typing import Any

import pandas as pd

from utils import crud, filters, parser, stats, utils, visuals

HEADER = """=== Terramotos ==="""

EVENT_COLS = [
    "Data",
    "Latitude",
    "Longitude",
    "Profundidade",
    "Tipo Evento",
    "Gap",
    "Magnitudes",
    "Regiao",
    "Sentido",
    "Pub",
    "SZ",
    "VZ",
]
STATION_COLS = [
    "Estacao",
    "Hora",
    "Min",
    "Seg",
    "Componente",
    "Distancia Epicentro",
    "Tipo Onda",
]

MENU = """[1] Criar a base de dados
[2] Apagar um evento
[3] Apagar uma entrada de um evento
[4] Visualizar um evento
[5] Guardar como JSON
[6] Guardar como CSV
[7] Estatísticas
[8] Criar uma entrada
[9] Gráficos
[10] Filtros (T7)

[Q] Sair
"""


def guardar_csv(df: pd.DataFrame, fname: str):
    """Guarda uma DataFrame num ficheiro csv

    Args:
        df (pd.DataFrame): Dataframe com os dados
        fname (str): nome do ficheiro csv

    Returns:
        bool: Retorna se a operação foi bem sucedida ou não
    """
    with open(fname, "w") as fp:
        try:
            df.to_csv(fp, index=False)
        except ValueError:
            return False
    return True


def main():
    """Ponto de entrada do programa.

    Constituido por um while loop a correr um menu onde o utilizador pode
    interagir com os vários módulos implementados.

    """
    isRunning = True
    db = None
    original_db = None

    retInfo = None

    while isRunning:
        os.system("cls" if sys.platform == "windows" else "clear")
        print(HEADER + "\n" + MENU)
        usrIn = input("Opção: ").lower()

        match usrIn:
            case "1":
                fname = _get_usr_input("Qual os dados a ler? (dados.txt por defeito): ")
                if fname is None:
                    fname = "dados.txt"

                if _file_exists(fname) and fname.endswith(".json"):
                    db = pd.read_json(fname)
                    original_db = db.copy()
                    print("Base de dados populada.")
                elif _file_exists(fname):
                    db = parser.parse(fname)
                    original_db = db.copy()
                    input("Base de dados populada. Enter para voltar ao menu inicial")
                else:
                    input("Base de dados não encontrada. Por favor tenta de novo.")

            case "2":
                if db is not None:
                    crud.read_ids(db)
                    choice: int = _get_usr_input("Escolhe o ID para apagar: ", int)

                    if not _event_exists(db, choice):
                        retInfo = "ID do event não encontrado!"

                    else:
                        db = crud.delete_event(db, choice)
                        input()

                else:
                    retInfo = "Base de dados não encontrada!"

            case "3":
                if db is not None:
                    crud.read_ids(db)
                    eid_choice: int = _get_usr_input("Escolhe o ID: ", int)

                    if not _event_exists(db, eid_choice):
                        retInfo = "ID do event não encontrado!"

                    else:
                        os.system("cls" if sys.platform == "windows" else "clear")
                        table = crud.get_table(db, eid_choice)
                        _prettify_event(table)
                        crud.show_table(table)

                        row_choice = _get_usr_input("Escolhe a linha a apagar:", int)

                        db, msg = crud.delete_table_row(db, eid_choice, row_choice)
                        new_table = crud.get_table(db, eid_choice)
                        crud.show_table(new_table)
                        print(msg)
                        input()
                else:
                    retInfo = "Base de dados não encontrada!"

            case "4":
                if db is not None:
                    crud.read_ids(db)
                    choice = _get_usr_input("Escolhe o ID para ver os dados: ", int)

                    if not _event_exists(db, choice):
                        retInfo = "ID do event não encontrado!"

                    else:
                        os.system("cls" if sys.platform == "windows" else "clear")
                        table = crud.get_table(db, choice)
                        _prettify_event(table)
                        crud.show_table(table)
                        input()

                else:
                    retInfo = "Base de dados não encontrada!"

            case "5":
                if db is not None:
                    fname = _get_usr_input("Nome do ficheiro a guardar? ")
                    if fname is None:
                        fname = "valores.json"
                        utils.save_as_json(db, fname, EVENT_COLS)
                else:
                    retInfo = "Base de dados não encontrada!"

            case "6":
                if db is not None:
                    fname = _get_usr_input("Nome do ficheiro a guardar? ")
                    if fname is None:
                        fname = "valores.csv"
                    guardar_csv(db, fname)
                else:
                    retInfo = "Base de dados não encontrada!"

            case "7":
                if db is not None:
                    stats.stat_menu(db)
                else:
                    retInfo = "Base de dados não encontrada!"

            case "8":
                if db is not None:
                    crud.read_ids(db)
                    eid_choice = _get_usr_input("Escolhe o ID: ", int)

                    if not _event_exists(db, eid_choice):
                        retInfo = "ID do event não encontrado!"

                    else:
                        os.system("cls" if sys.platform == "windows" else "clear")
                        table = crud.get_table(db, eid_choice)
                        _prettify_event(table)
                        crud.show_table(table)

                        insertion_point = _get_usr_input("Posição da nova linha: ", int)

                        db, msg = crud.create_table_row(db, eid_choice, insertion_point)
                        new_table = crud.get_table(db, eid_choice)
                        crud.show_table(new_table)
                        print(msg)
                        input()
                else:
                    retInfo = "Base de dados não encontrada!"

            case "9":
                if db is not None:
                    visuals.visual_menu(db)
                else:
                    retInfo = "Base de dados não encontrada!"

            case "10":
                if db is not None:
                    # Passa db e original_db para o menu de filtros
                    # Retorna a nova db ativa (filtrada ou redefinida)
                    db = filters.filter_menu(db, original_db)
                else:
                    retInfo = "Base de dados não encontrada!"

            case "q":
                isRunning = False
                continue
            case _:
                pass

        if retInfo:
            print(retInfo)
            retInfo = None
            input("Clique Enter para continuar")


def _file_exists(name: str) -> bool:
    """Verifica se um ficheiro existe no diretório onde o programa correntemente
    corre, através de os.getcwd()

    Args:
        name (str): Nome do ficheiro a verificar

    Returns:
        bool: True se existe, False caso contrário
    """
    currFiles = os.listdir(os.getcwd())
    if name in currFiles:
        return True
    return False


def _event_exists(df: pd.DataFrame, eid: int) -> bool:
    """Função privada de verificação de eventos

    Verifica se um certo ID de evento existe ou não dentro de uma DataFrame

    Args:
        df (pd.DataFrame): DataFrame a pesquisar
        eid (int): Evento específico a pesquisar

    Returns:
        bool: True se evento existe dentro da DataFrame, False caso contrário
    """
    allEvents = set(df["ID"])
    return eid in allEvents


def _get_usr_input(msg: str, asType: Any = str) -> Any:
    """Modifica o stdin do utilizador para o tipo especificado. Por defeito retorna uma str.

    Args:
        msg (str): String a ser alterada
        asType (Any): tipo no qual msg deverá ser intepretado como (default: `str`)

    Returns:
        [type]: [description]
    """
    usrIn = input(msg)

    if usrIn == "":
        return None
    return asType(usrIn)


def _prettify_event(df: pd.DataFrame) -> None:
    """Função privada para utilização na visualização de um evento singular através
    do menu de `Visualizar um evento`

    Args:
        df (pd.DataFrame): DataFrame com os dados do evento
    """
    # preambleInfo = df.drop_duplicates(subset="ID", keep="first")
    # stations = df[["Estacao", "Componente", "Tipo Onda", "Amplitude"]]
    info = df.drop_duplicates(subset="Data", keep="first")
    data = datetime.fromisoformat(info.Data.values[0]).strftime("%c")
    print(
        f"Região: {info['Regiao'].values[0]}\nData: {data}\nLatitude: {info['Latitude'].values[0]}\nLongitude: {info['Longitude'].values[0]}"
        + f"\nProfundidade: {info['Profundidade'].values[0]}\nTipo de evento: {info['Tipo Evento'].values[0]}\n"
    )


# entry point
if __name__ == "__main__":
    main()
