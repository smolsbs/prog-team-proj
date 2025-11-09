# pyright: basic

import pandas as pd
from . import parser

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

HEADER_COLS = ["Data", "Distancia", "Tipo Ev", "Lat", "Long", "Prof", "Magnitudes"]
TABLE_READ_RET = ["Data", "Lat", "Long", "Distancia", "Tipo Ev", "Amplitude"]

def _get_uniques(df) -> pd.DataFrame:
    return df.get(["ID", "Data", "Regiao"]).drop_duplicates(subset="ID", keep="first")

def _show_events(df):
    for (_, row) in df.iterrows():
        print(f"{row["ID"]}: {row["Regiao"]}")

def read_ids(df):
    ids = _get_uniques(df)
    _show_events(ids)

def get_unique_events_table(df):
    return df.drop_duplicates(subset="ID", keep="first")

def read_header(df, event_id):
    # Informações do header do evento
    row = df[df["ID"] == event_id].iloc[0]
    cols = list(df.columns)
    # end = cols.index("ID") - 1
    # header_cols = cols[:end]
    # Para selecionar todas as colunas em vez de só algumas
    info = []
    for (i, col) in enumerate(HEADER_COLS):
        info.append(f"{i+1} {col}: {row[col]}")
    infoString = f"Header do evento {event_id}:\n" + "\n".join(info) 
    return infoString

def show_table(df, retCols=TABLE_READ_RET):
    print(df.loc[:,retCols])

def get_table(df, event_id):
    rows = df[df["ID"] == event_id]
    rows = rows.drop("ID", axis=1)
    return rows


def read_table_row(df, event_id, row_number_1):
    # retorna uma linha específica da tabela
    row_number_0 = row_number_1 - 1
    table = get_table(df, event_id)
    if row_number_0 < 0 or row_number_0 >= len(table):
        return f"Linha {row_number_1} não pertence ao evento {event_id}."
    row = table.iloc[row_number_0]
    cols = list(df.columns)
    start = cols.index("Estacao")
    tableCols = cols[start:]
    info = []
    for (i, col) in enumerate(tableCols):
        info.append(f"{i+1} {col}: {row[col]}")
    return f"Linha {row_number_1:02d} do evento {event_id}:\n" + "\n".join(info) 

def update_table_row(df, row_line, new_data):
    for key, value in new_data.items():
        if key in df.columns:
            df.loc[row_line, key] = value
    return f"Linha {row_line} do evento atualizada com sucesso."

def update_header(df, event_id, new_data):
    # atualiza o header de um evento
    for key, value in new_data.items():
        if key in df.columns:
            df.loc[(df["ID"] == event_id) | df.iloc[0], key] = value
    return f"Header do evento {event_id} atualizado com sucesso."

def delete_event(df, event_id):
    # Apaga um evento inteiro (header + tabela)
    new_df = df.drop(df[df["ID"] == event_id].index)
    print(f"Evento {event_id} apagado!")
    return new_df

def delete_table_row(df, event_id, row_number):
    # Apaga uma linha específica da tabela do evento
    new_df = df.drop([row_number]).reset_index(drop=True)
    return new_df

def create_blank_event(df, event_id):
    # Criar um evento vazio com linha de header e 1 linha de coluna
    df.loc[df["ID"] >= event_id, "ID"] += 1

    blank_row_df = pd.DataFrame(columns=df.columns, index=[0, 1])
    blank_row_df["ID"] = event_id
    blank_row_df = blank_row_df.astype(df.dtypes)

    new_df = pd.concat([df, blank_row_df], ignore_index=True)
    new_df = new_df.sort_values(by="ID", kind="mergesort").reset_index(drop=True)

    return new_df

    
def create_table_row(df, event_id, row_number_1):
    event_rows = df[df["ID"] == event_id]
    if event_rows.empty:
        return df, f"Erro: Evento com ID {event_id} não encontrado."

    header_idx = event_rows.index[0]
    table_size = len(event_rows.index) - 1

    # Validar posição da nova linha
    if not (1 <= row_number_1 <= table_size + 1):
        return df, f"Erro: Posição {row_number_1} inválida. Evento {event_id} tem {table_size} linha(s) na tabela."
    insertion_point = header_idx + row_number_1

    new_row_df = pd.DataFrame(columns=df.columns, index=[0])
    new_row_df['ID'] = event_id
    new_row_df = new_row_df.astype(df.dtypes)
    df_before = df.iloc[:insertion_point]
    df_after = df.iloc[insertion_point:]

    new_df = pd.concat([df_before, new_row_df, df_after], ignore_index=True)

    return new_df, f"Linha inserida com sucesso na posição {row_number_1} do evento {event_id}."

def create_entire_database() -> pd.DataFrame:
    pass

