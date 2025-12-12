# pyright: basic

import pandas as pd

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

# -- globals

HEADER_COLS = ["Data", "Distancia", "Tipo Evento", "Latitude", "Longitude", "Profundidade", "Magnitudes"]
TABLE_READ_RET = ["Estacao", "Hora", "Min", "Seg", "Componente", "Amplitude"]

# -- helper funcs

def _get_uniques(df) -> pd.DataFrame:
    return df.get(["ID", "Data", "Regiao"]).drop_duplicates(subset="ID", keep="first")


def _show_events(df):
    for (_, row) in df.iterrows():
        print(f"{row["ID"]}: {row["Regiao"]}")

# -- main

def read_ids(df):
    ids = _get_uniques(df)
    _show_events(ids)


def get_unique_events_table(df):
    return df.drop_duplicates(subset="ID", keep="first")


def read_header(df, event_id):
    # Obtém a informação da primeira linha do evento (cabeçalho)
    row = df[df["ID"] == event_id].iloc[0]
    cols = list(df.columns)

    info = []
    for (i, col) in enumerate(HEADER_COLS):
        # Constrói a string formatada "Índice Nome: Valor"
        info.append(f"{i+1} {col}: {row[col]}")
    infoString = f"Header do evento {event_id}:\n" + "\n".join(info) 
    return infoString


def show_table(df, retCols=TABLE_READ_RET):
    print(df.loc[:,retCols])


def get_table(df, event_id):
    rows = df[df["ID"] == event_id]
    return rows


def read_table_row(df, event_id, row_number_1):
    # Retorna uma linha específica da tabela de estações
    # row_number_1 é o índice dado pelo utilizador (começa em 1)
    # row_number_0 é o índice real da lista (começa em 0)
    row_number_0 = row_number_1 - 1
    table = get_table(df, event_id)
    
    # Verifica se a linha pedida existe dentro das linhas deste evento
    if row_number_0 < 0 or row_number_0 >= len(table):
        return f"Linha {row_number_1} não pertence ao evento {event_id}."
        
    row = table.iloc[row_number_0]
    cols = list(df.columns)
    
    # Encontra onde começam as colunas da estação para mostrar apenas os dados relevantes
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
    # Atualiza o cabeçalho de um evento com os novos dados
    for key, value in new_data.items():
        if key in df.columns:
            # Atualiza todas as linhas deste evento (ID == event_id) com o novo valor
            df.loc[(df["ID"] == event_id) | df.iloc[0], key] = value
    return f"Header do evento {event_id} atualizado com sucesso."


def delete_event(df, event_id):
    # Apaga um evento inteiro (header + tabela)
    new_df = df.drop(df[df["ID"] == event_id].index)
    print(f"Evento {event_id} apagado!")
    return new_df


def delete_table_row(df, event_id, row_number):
    # Apaga uma linha específica da tabela de estações de um evento
    
    # Encontra todos os índices (números de linha no DataFrame que pertencem a este evento
    matching_indices = df.index[df['ID'] == event_id].tolist()

    first_event_row = matching_indices[0]
    last_event_row = matching_indices[-1]

    # Garante que não estamos a apagar uma linha que pertence a outro evento
    if row_number < first_event_row or row_number > last_event_row:
        return df, f"Erro: A posição a apagar, {row_number} está fora do intervalo permitido para o evento {event_id}."
    
    new_df = df.drop([row_number]).reset_index(drop=True)
    return new_df, f"Linha {row_number} apagada com sucesso!"


def create_blank_event(df, event_id):
    # Cria um novo evento vazio
    # Primeiro, avança os IDs de todos os eventos seguintes para arranjar espaço
    df.loc[df["ID"] >= event_id, "ID"] += 1

    # Cria 2 linhas novas: uma para o cabeçalho e outra vazia para dados
    blank_row_df = pd.DataFrame(columns=df.columns, index=[0, 1])
    blank_row_df["ID"] = event_id
    blank_row_df = blank_row_df.astype(df.dtypes)

    # Junta as novas linhas ao dataframe principal
    new_df = pd.concat([df, blank_row_df], ignore_index=True)
    # Ordena por ID para garantir que fica tudo na ordem certa (mergesort é estável)
    new_df = new_df.sort_values(by="ID", kind="mergesort").reset_index(drop=True)

    return new_df


def create_table_row(df, event_id, insertion_point):
    # Insere uma nova linha vazia numa posição específica dentro do evento
    
    # Encontra os limites (início e fim) do evento atual
    matching_indices = df.index[df['ID'] == event_id].tolist()

    first_event_row = matching_indices[0]
    last_event_row = matching_indices[-1]

    # Valida se o ponto de inserção é válido para este evento
    if insertion_point < first_event_row or insertion_point > last_event_row + 1:
        return df, f"Erro: A posição de inserção {insertion_point} está fora do intervalo permitido para o evento {event_id}"

    # Cria a nova linha
    new_row_df = pd.DataFrame(columns=df.columns, index=[0])
    new_row_df['ID'] = event_id
    new_row_df = new_row_df.fillna(0)
    new_row_df = new_row_df.astype(df.dtypes)
    
    # Parte o dataframe em dois (antes e depois do ponto de inserção) e mete a nova linha no meio
    df_before = df.iloc[:insertion_point]
    df_after = df.iloc[insertion_point:]

    new_df = pd.concat([df_before, new_row_df, df_after], ignore_index=True)

    return new_df, f"Linha inserida com sucesso na posição {insertion_point}"

def create_entire_database() -> pd.DataFrame:
    pass

def create_table_row_old(df, event_id, row_number_1):
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

