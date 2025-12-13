# Project I - Earthquakes

## Como utilizar
Correr o ficheiro `earthquakes.py` usando `python earthquakes.py`
Garantir que o ficheiro de dados está no mesmo diretório que o ficheiro `earthquakes.py`

## Objectivos

First, let's represent the data using Python's Pandas module and implement CRUD operations, including JSON's conversion. Then, let's implement some statistical operations with graphical representations using Python's Matplotlib module over data representation in Pandas data model.

## Tarefas:

- T1 - Convert data structure in file (MS Excel) to the Panda's data structure and save it in a text file;
- T2 - Implement CRUD operations through a text menu;
- T3 - Implement statistical operations such as: average, variance, standard desviation, max, min, mode; through a text menu;
- T4 - Convert from Pandas to JSON and save it in a text file;
- T5 - Calcular as seguintes estatísticas:
  - Número de eventos por dia e por mês.
  - Média e desvio padrão da profundidade e da magnitude por mês.
  - Mediana, 1º quartil e  3º quartil da profundidade e da magnitude por mês.
  - Máximo e mínimo a profundidade e da magnitude por mês.
- T6 - Para a representação gráfica:
  - Um gráfico de barras com o numero de eventos por dia.
  - Um gráfico de barras com o numero de eventos por mês.
  - Um gráfico linear com a média +/- o desvio padrão das profundidades por mês.
  - Um gráfico linear com a média +/- a desvio padrão da magnitude L por mês.
  - Um gráfico tipo "boxplot" com as profundidades por mês.
  - Um gráfico tipo "boxplot" com as magnitudes L por mês.
- T7 - Implementar os filtros de seleção de eventos para o cálculo / representação gráfica:
  - Período temporal (Data inicial, Data final).
  - Eventos com GAP menor que um determinado valor.
  - Qualidade (EPI ou Todos).
  - Zonas SZ.
  - Zonas VZ.
  - Limitar por Magnitudes L (mínimo, máximo).
  - Limitar Profundidades  (mínimo, máximo).

## Prazos
- T1 a T4 -> 10 de novembro
- T5 a T7 -> 14 de dezembro

## Apontamentos
Dados parecem estar no formato [Nordic](https://seisan.info/v13/node259.html)

## Bibliografia
- [Pandas lib](https://pandas.pydata.org/docs)
- [Matplotlib](https://matplotlib.org/stable/index.html)
- [definição de CRUD](https://en.wikipedia.org/w/index.php?title=Create,_read,_update_and_delete&useskin=vector)
