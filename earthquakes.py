#! /usr/bin/env python
# pyright: basic

import json
import os

import pandas as pd

from utils import parser, crud, stats

HEADER = """=== Terramotos ==="""

MENU ="""[1] Criar a base de dados
[2] Atualizar uma entrada
[3] Apagar um evento
[4] Apagar uma entrada de um evento
[5] Visualizar uma entrada
[6] Guardar como JSON
[7] Guardar como CSV
[8] Estatísticas

[Q] Sair
"""

def guardar_df(df: pd.DataFrame, fname: str) -> bool:
    with open(fname, "w") as fp:
        fname = f"{fname}.txt"
        try:
            fp.write(df.to_string())
        except ValueError:
            return False
    return True


def guardar_json(df: pd.DataFrame, fname: str) -> bool:
    with open(fname , "w") as fp:
        try:
            json.dump(df.to_json(), fp)
        except:
            return False
    return True


def guardar_csv(df: pd.DataFrame, fname: str):
    with open(fname, "w") as fp:
        try:
            df.to_csv(fp, index=False)
        except ValueError:
            return False
    return True


def main():
    isRunning = True
    db = None
    
    retInfo = None

    while isRunning:
        os.system("cls")
        print(HEADER + "\n" + MENU)
        usrIn = input("Opção: ").lower()

        match usrIn:
            case "1":
                fname = _get_usr_input("Qual os dados a ler? (dados.txt por defeito): ")
                if fname is None:
                    fname = "dados.txt"

                if _file_exists(fname):
                    db = parser.parse(fname)
                    input("Base de dados populada. Enter para voltar ao menu inicial")
                else:
                    input("Base de dados não encontrada. Por favor tenta de novo.")

            case "2":
                if db is not None:
                    continue
                else:
                    retInfo = "Base de dados não encontrada!"

            case "3":
                if db is not None:
                    crud.read_ids(db)
                    choice = _get_usr_input("Escolhe o ID para apagar: ", int)

                    if not _event_exists(db, choice):
                        retInfo = "ID do event não encontrado!"

                    else:
                        db = crud.delete_event(db, choice)
                        input()

                else:
                    retInfo = "Base de dados não encontrada!"


            case "4":
                if db is not None:
                    crud.read_ids(db)
                    eid_choice = _get_usr_input("Escolhe o ID: ", int)

                    if not _event_exists(db, eid_choice):
                        retInfo = "ID do event não encontrado!"

                    else:
                        table = crud.get_table(db, eid_choice)
                        crud.show_table(table)
                        row_choice = _get_usr_input("Escolhe a linha a apagar:", int)
                        db = crud.delete_table_row(db, eid_choice, row_choice)
                        new_table = crud.get_table(db, eid_choice)
                        crud.show_table(new_table)
                        print(f"Linha {row_choice} apagada com sucesso!")
                        input()

                else:
                    retInfo = "Base de dados não encontrada!"

            case "5":
                if db is not None:
                    crud.read_ids(db)
                    choice = _get_usr_input("Escolhe o ID para ver os dados: ", int)

                    if not _event_exists(db, choice):
                        retInfo = "ID do event não encontrado!"

                    else:
                        table = crud.get_table(db, choice)
                        crud.show_table(table)
                        input()

                else:
                    retInfo = "Base de dados não encontrada!"

            case "6":
                if db is not None:
                    fname = _get_usr_input("Nome do ficheiro a guardar?")
                    if fname is None:
                        fname = "valores.json"
                    guardar_json(db, fname)
                else:
                    retInfo = "Base de dados não encontrada!"

            case "7":
                if db is not None:
                    fname = _get_usr_input("Nome do ficheiro a guardar?")
                    if fname is None:
                        fname = "valores.csv"
                    guardar_csv(db, fname)
                else:
                    retInfo = "Base de dados não encontrada!"

            case "8":
                if db is not None:
                    pass
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
    currFiles = os.listdir(os.getcwd())
    if name in currFiles:
        return True
    return False

def _event_exists(df, eid) -> bool:
    allEvents = set(df["ID"])
    return eid in allEvents


def _get_usr_input(msg:str, asType=str):
    usrIn = input(msg)

    if usrIn == "":
        return None
    return asType(usrIn)


if __name__ == '__main__':
    main()
