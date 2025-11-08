#! /usr/bin/env python
# pyright: basic

import json
import os

import pandas as pd

import parser
import crud

HEADER = """=== Terramotos ==="""

MENU ="""[1] Criar a base de dados
[2] Atualizar uma entrada
[3] Apagar uma entrada
[4] Visualizar uma entrada

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
    db = parser.parse("dados.txt")
    retInfo = None

    while isRunning:
        os.system("cls")
        print(HEADER + "\n" + MENU)
        usrIn = input("Opção: ").lower()

        match usrIn:
            case "1":
                os.system("cls")
                print(HEADER + "\nCRIAR")
                fname = input("Nome do ficheiro com os dados. (Branco para dados.txt)")
                if fname == "":
                    fname = "dados.txt"
                if _file_exists(fname):
                    db = parser.parse(fname)
                else:
                    retInfo = "Nenhum ficheiro encontrado!"

            case "2":
                if db is not None:
                    continue
                else:
                    retInfo = "Base de dados não encontrada!"

            case "3":
                if db is not None:
                    a = _get_uniques(db)
                    ev_ids = _show_events(a)

                    _select = input("Qual a entrada a apagar: ")

                    db = db.drop(db[db["ID"] == ev_ids[_select]].index)

                else:
                    retInfo = "Base de dados não encontrada!"

            case "4":
                if db is not None:
                    a = _get_uniques(db)
                    ev_ids = _show_events(a)

                    _select = input("Qual a entrada a visualizar: ")
                    _view_event(db, ev_ids[_select])

                    input()

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

def _get_uniques(df) -> pd.DataFrame:
    return df.get(["ID", "Data", "Regiao"]).drop_duplicates(subset="ID", keep="first")

def _show_events(df):
    events = {}
    idx = 1
    for (_, row) in df.iterrows():
        print(f"{idx:2d}| {row["Regiao"]}")
        events[str(idx)] = row["ID"]
        idx += 1
    return events

def _view_event(df, id):
    for idx, row in df.loc[df["ID"] == id ].iterrows():
        print(row)



if __name__ == '__main__':
    main()
