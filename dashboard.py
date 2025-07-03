import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# Carregar a planilha
df = pd.read_excel("ProjectEmExcel_MKE.xlsx")

# Selecionar e preparar colunas
df = df[[
    "Número Hierárquico", "Nome da Tarefa",
    "%concluida prev. (Número10)", "% Concluída",
    "Responsável 01", "Responsável 02", "Nomes de Recursos"
]].copy()

df.columns = ["hierarquia", "tarefa", "previsto", "concluido", "responsavel 1", "responsavel 2", "nome dos recursos"]

df["previsto"] = pd.to_numeric(df["previsto"], errors="coerce").fillna(0)
df["concluido"] = pd.to_numeric(df["concluido"], errors="coerce").fillna(0)

# Criar path da hierarquia para AgGrid (como lista)
df["hierarchy_path"] = df["hierarquia"].astype(str).apply(lambda x: x.split("."))

# Mostrar como dashboard
st.set_page_config(page_title="Dashboard com Hierarquia", layout="wide")
st.title("📊 Acompanhamento Geral Macaé")
st.markdown("Explore o andamento das tarefas.")

# Montar opções de visualização
gb = GridOptionsBuilder.from_dataframe(df)

# Ativar modo árvore (treeData)
gb.configure_grid_options(
    treeData=True,
    animateRows=True,
    groupDefaultExpanded=0,  # -1: tudo expandido, 0: tudo recolhido inicialmente
    getDataPath=JsCode("function(data) { return data.hierarchy_path; }")
)

# Esconder colunas auxiliares
gb.configure_columns(["hierarquia", "hierarchy_path"], hide=True)

# valor em percentual 
percent_formatter_decimal = JsCode("function(params) { return (params.value * 100).toFixed(1) + '%'; }")
percent_formatter_direct = JsCode("function(params) { return (params.value).toFixed(1) + '%'; }")

# Ajustar colunas principais
gb.configure_column("tarefa", header_name="Tarefa", flex=3)
gb.configure_column("previsto", header_name="% Previsto", type=["numericColumn"], maxWidth=120, valueFormatter=percent_formatter_direct)
gb.configure_column("concluido", header_name="% Concluído", type=["numericColumn"], maxWidth=120, valueFormatter=percent_formatter_decimal)
gb.configure_column("responsavel 1", header_name="Responsável 1", maxWidth=120)
gb.configure_column("responsavel 2", header_name="Responsável 2", maxWidth=120)
gb.configure_column("nome dos recursos", header_name="Recurso", maxWidth=120)

# Exibir grid
AgGrid(
    df,
    gridOptions=gb.build(),
    height=450,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=True,
    fit_columns_on_grid_load=True
)
