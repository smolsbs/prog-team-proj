# pyright: basic

from typing import Any

import pandas as pd

pd.set_option("display.max_rows", 500)
pd.set_option("display.max_columns", 500)
pd.set_option("display.width", 150)

# -- globals

HEADER_COLS = [
    "Data",
    "Distancia",
    "Tipo Evento",
    "Latitude",
    "Longitude",
    "Profundidade",
    "Magnitudes",
]
TABLE_READ_RET = ["Estacao", "Hora", "Min", "Seg", "Componente", "Amplitude"]

# -- helper funcs


def _get_uniques(df: pd.DataFrame) -> pd.DataFrame:
    """Funcao privada que retorna os eventos unicos, removendo duplicados.

    Mantem o primeiro evento de cada ID unico, removendo entradas com o ID igual

    Args:
        df (pd.DataFrame): DataFrame com os dados

    Returns:
        pd.DataFrame: Nova DataFrame com IDs duplicados removidos
    """
    return df.get(["ID", "Data", "Regiao"]).drop_duplicates(subset="ID", keep="first")


def _show_events(df: pd.DataFrame) -> None:
    """Funcao privada para print de cada evendo e a respectiva Regiao

    Args:
        df (pd.DataFrame): DataFrame com os dados
    """
    for _, row in df.iterrows():
        print(f"{row['ID']}: {row['Regiao']}")


# -- main


def read_ids(df: pd.DataFrame) -> None:
    """Mostra, por print(), os eventos disponiveis em df.

    Args:
        df (pd.DataFrame): DataFrame com os dados
    """
    ids = _get_uniques(df)
    _show_events(ids)


def get_unique_events_table(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna uma nova DataFrame com eventos de ID unico.

    Remove, para cada ID unico, os duplicados, mantendo o primeiro.

    Args:
        df (pd.DataFrame): DataFrame com os dados

    Returns:
        pd.DataFrame: Nova DataFrame filtrada
    """
    return df.drop_duplicates(subset="ID", keep="first")


def read_header(df: pd.DataFrame, event_id: int) -> str:
    """Lê a primeira entrada com ID `event_id`

    Obtém a informação da primeira linha do evento (cabeçalho) e
    constrói a string formatada "<indice> <nome>: <valor>"

    Args:
        df (pd.DataFrame): DataFrame com os dados
        event_id (int): ID do evento

    Returns:
        str: str com os dados do evento
    """
    row = df[df["ID"] == event_id].iloc[0]

    info = []
    for i, col in enumerate(HEADER_COLS):
        info.append(f"{i + 1} {col}: {row[col]}")

    infoString = f"Header do evento {event_id}:\n" + "\n".join(info)
    return infoString


def show_table(df: pd.DataFrame, retCols: list[str] = TABLE_READ_RET) -> None:
    """print() da DataFrame total, filtrada por colunas. Por defeito, faz print
    de apenas da Estação, HMS, Componente e Amplitude registada

    Args:
        df (pd.DataFrame): DataFrame com os dados
        retCols (list[str]): Filtro de colunas a fazer print() (default: `TABLE_READ_RET`)
    """
    print(df.loc[:, retCols])


def get_table(df: pd.DataFrame, event_id: int) -> pd.DataFrame:
    """Retorna uma DataFrame apenas com o evento `event_id`

    Args:
        df (pd.DataFrame): DataFrame com os dados
        event_id (int): ID do evento

    Returns:
        pd.DataFrame: Nova DataFrame com todos os dados do evento `event_id`
    """
    rows: pd.DataFrame = df[df["ID"] == event_id]  # type: ignore
    return rows


def delete_event(df: pd.DataFrame, event_id: int) -> pd.DataFrame:
    """Apaga um evento da DataFrame, retornando a DataFrame atualizada

    Args:
        df (pd.DataFrame): DataFrame com os dados
        event_id (int): ID do evento a apagar

    Returns:
        pd.DataFrame: DataFrame sem o evento.
    """
    new_df = df.drop(df[df["ID"] == event_id].index)
    print(f"Evento {event_id} apagado!")
    return new_df


def delete_table_row(df: pd.DataFrame, event_id: int, row_number: int) -> pd.DataFrame:
    """Apaga uma linha específica relativa ao evento `event_id`

    Args:
        df (pd.DataFrame): DataFrame com os dados
        event_id ([type]): [description]
        row_number ([type]): [description]

    Returns:
        pd.DataFrame: [description]
    """
    matching_indices = df.index[df["ID"] == event_id].tolist()

    first_event_row = matching_indices[0]
    last_event_row = matching_indices[-1]

    # Garante que não estamos a apagar uma linha que pertence a outro evento
    if row_number < first_event_row or row_number > last_event_row:
        print(
            f"Erro: A posição a apagar, {row_number} está fora do intervalo permitido para o evento {event_id}."
        )
        return df

    new_df = df.drop([row_number]).reset_index(drop=True)
    print(f"Linha {row_number} apagada com sucesso!")
    return new_df


def create_table_row(
    df: pd.DataFrame, event_id: int, insertion_point: int
) -> pd.DataFrame:
    """Insere uma nova linha vazia numa posição específica dentro do evento `event_id`

    Args:
        df (pd.DataFrame): DataFrame com os dados
        event_id (int): ID do evento
        insertion_point (int): [description]

    Returns:
        tuple: [description]
    """
    #

    # Encontra os limites (início e fim) do evento atual
    matching_indices = df.index[df["ID"] == event_id].tolist()

    first_event_row = matching_indices[0]
    last_event_row = matching_indices[-1]

    # Valida se o ponto de inserção é válido para este evento
    if insertion_point < first_event_row or insertion_point > last_event_row + 1:
        print(
            f"Erro: A posição de inserção {insertion_point} está fora do intervalo permitido para o evento {event_id}"
        )
        return df

    # Cria a nova linha
    new_row_df = pd.DataFrame(columns=df.columns, index=[0])
    new_row_df["ID"] = event_id
    new_row_df = new_row_df.fillna(0)
    new_row_df = new_row_df.astype(df.dtypes)

    # Parte o dataframe em dois (antes e depois do ponto de inserção) e mete a nova linha no meio
    df_before = df.iloc[:insertion_point]
    df_after = df.iloc[insertion_point:]

    new_df = pd.concat([df_before, new_row_df, df_after], ignore_index=True)
    print(f"Linha inserida com sucesso na posição {insertion_point}")

    return new_df


# -- Deprecated


def update_header(df, event_id, new_data):
    """>OBSOLETO<

    Atualiza o cabeçalho de um evento com os novos dados

    Args:
        df (pd.DataFrame): DataFrame com os dados
        event_id (int): ID do evento
        new_data (dict[str, Any]): Novos dados para substituir

    Returns:
        str: AWK de atualização do cabeçalho
    """
    for key, value in new_data.items():
        if key in df.columns:
            # Atualiza todas as linhas deste evento (ID == event_id) com o novo valor
            df.loc[(df["ID"] == event_id) | df.iloc[0], key] = value
    return f"Header do evento {event_id} atualizado com sucesso."


def create_table_row_old(
    df: pd.DataFrame, event_id: int, row_number_1: int
) -> pd.DataFrame:
    """>OBSOLETO<

    Cria uma linha na DataFrame

    Args:
        df (pd.DataFrame): DataFrame com os dados
        event_id (int): ID do evento
        row_number_1 (int): posição livre onde inserir

    Returns:
        pd.DataFrame: Nova DataFrame
    """
    event_rows = df[df["ID"] == event_id]
    if event_rows.empty:
        print(f"Erro: Evento com ID {event_id} não encontrado.")
        return df
    header_idx: int = event_rows.index[0]  # type: ignore
    table_size = len(event_rows.index) - 1

    # Validar posição da nova linha
    if not (1 <= row_number_1 <= table_size + 1):
        print(
            f"Erro: Posição {row_number_1} inválida. Evento {event_id} tem {table_size} linha(s) na tabela."
        )
        return df

    insertion_point = header_idx + row_number_1

    new_row_df = pd.DataFrame(columns=df.columns, index=[0])
    new_row_df["ID"] = event_id
    new_row_df = new_row_df.astype(df.dtypes)
    df_before = df.iloc[:insertion_point]
    df_after = df.iloc[insertion_point:]

    new_df = pd.concat([df_before, new_row_df, df_after], ignore_index=True)

    print(f"Linha inserida com sucesso na posição {row_number_1} do evento {event_id}.")
    return new_df


def create_blank_event(df: pd.DataFrame, event_id: int) -> pd.DataFrame:
    """>OBSOLETO<

    Criano um novo evento com valores vazios

    Args:
        df (pd.DataFrame): DataFrame com os dados
        event_id (int): ID do novo evento

    Returns:
        pd.DataFrame: Nova DataFrame
    """
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


def update_table_row(df: pd.DataFrame, row_line: int, new_data: dict[str, Any]) -> str:
    """Atualiza uma linha de `df` com novos dados

    Args:
        df (pd.DataFrame): DataFrame com os dados
        row_line (int): linha a atualizar
        new_data (dict[str, Any]): novos dados a substituir na linha

    Returns:
        str: AWK de atualização da linha
    """
    for key, value in new_data.items():
        if key in df.columns:
            df.loc[row_line, key] = value
    return f"Linha {row_line} do evento atualizada com sucesso."


def read_table_row(df: pd.DataFrame, event_id: int, row_number_1: int) -> str:
    """Retorna uma str com todos os valores de uma linha de `df`, relativa ao
    evento `event_id`.

    Args:
        df (pd.DataFrame): DataFrame com os dados
        event_id (int): ID do evento
        row_number_1 (int): Linha a imprimir

    Returns:
        str: String formatada com os dados.
    """
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
    for i, col in enumerate(tableCols):
        info.append(f"{i + 1} {col}: {row[col]}")
    return f"Linha {row_number_1:02d} do evento {event_id}:\n" + "\n".join(info)
