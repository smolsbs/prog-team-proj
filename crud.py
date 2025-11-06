import pandas as pd
import parser
import earthquakes as eq

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 150)

def read_ids(df):
    # Lista de IDs únicos no DataFrame
    return sorted(set(df["ID"]))

def read_header(df, event_id):
    # Informações do header do evento
    row = df[df["ID"] == event_id].iloc[0]
    cols = list(df.columns)
    headerCols = ["DateTime", "Distance Indicator", "Event ID", "Lat", "Long", "Depth", "Agency", "Magnitudes"]
    # end = cols.index("ID") - 1
    # header_cols = cols[:end]
    # Para selecionar todas as colunas em vez de só algumas
    info = []
    for (i, col) in enumerate(headerCols):
        info.append(f"{i+1} {col}: {row[col]}")
    infoString = f"Header do evento {event_id}:\n" + "\n".join(info) 
    return infoString


def get_table(df, event_id):
    # retorna a tabela de dados do evento
    rows = df[df["ID"] == event_id]
    cols = list(df.columns)
    start = cols.index("ID") + 1
    table = rows[cols[start:]].iloc[1:]
    return table

def read_table_row(df, event_id, row_number_1):
    # retorna uma linha específica da tabela
    row_number_0 = row_number_1 - 1
    table = get_table(df, event_id)
    if row_number_0 < 0 or row_number_0 >= len(table):
        return f"Linha {row_number_1} não pertence ao evento {event_id}."
    row = table.iloc[row_number_0]
    cols = list(df.columns)
    start = cols.index("STAT")
    tableCols = cols[start:]
    info = []
    for (i, col) in enumerate(tableCols):
        info.append(f"{i+1} {col}: {row[col]}")
        # TODO corrigir numeros acima de 10 arruinando o alinhamento
    infoString = f"Linha {row_number_1} do evento {event_id}:\n" + "\n".join(info) 
    return infoString

def update_table_row(df, event_id, row_number_1, new_data):
    # atualiza uma linha específica da tabela do evento
    row_number_0 = row_number_1 - 1
    table = get_table(df, event_id)
    if row_number_0 < 0 or row_number_0 >= len(table):
        return f"Linha {row_number_1} não pertence ao evento {event_id}."
    for key, value in new_data.items():
        if key in table.columns:
            df.loc[(df["ID"] == event_id) & (df.index == table.index[row_number_0]), key] = value
    return f"Linha {row_number_1} do evento {event_id} atualizada com sucesso."

def update_header(df, event_id, new_data):
    # atualiza o header de um evento
    for key, value in new_data.items():
        if key in df.columns:
            df.loc[(df["ID"] == event_id) | df.iloc[0], key] = value
    return f"Header do evento {event_id} atualizado com sucesso."

def delete_event(df, event_id):
    # Apaga um evento inteiro (header + tabela)
    new_df = df.drop(df[df["ID"] == event_id].index)
    new_df.loc[df["ID"] > event_id, "ID"] -= 1
    return new_df

def delete_table_row(df, event_id, row_number_1):
    # Apaga uma linha específica da tabela do evento
    row_number_0 = row_number_1 - 1
    table = get_table(df, event_id)
    if row_number_0 < 0 or row_number_0 >= len(table):
        return f"Linha {row_number_1} não pertence ao evento {event_id}."
    new_df = df.drop(table.index[row_number_0])
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

''' teste temporário enquanto não temnos menu
if __name__ == "__main__":
    df = parser.parse()
    first_id = read_ids(df)[0]
    for i in range(5):
        df = delete_event(df, i)
    for i in range(5):
        df = create_blank_event(df, i+5)
    update_table_row(df, 5, 1, {"Velo": 5.1})
    df, msg = insert_table_row(df, 5, 1)
    df, msg = insert_table_row(df, 5, 3)
    eq.guardar_csv(df, "dados.csv")
    eq.guardar_df(df, "data.txt")
'''