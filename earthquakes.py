#! /usr/bin/env python
import pandas as pd
import json
from parser import parse

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
    pass




if __name__ == '__main__':
    main()
