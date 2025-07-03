import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode  # <-- esta linha corrige o erro


# Carregar a planilha
df = pd.read_excel("ProjectEmExcel_MKE.xlsx")

# Selecionar e preparar colunas
df = df[[
    "Número Hierárquico", "Nome da Tarefa",
    "%concluida prev. (Número10)", "% Concluída",
    "Responsável 01", "Responsável 02", "Nomes de Recursos"
]].copy()

df.columns = ["hierarquia", "tarefa", "previsto", "concluido", "responsavel 1", "responsavel 2", "nome dos recursos"]

# Tratar dados numéricos
df["previsto"] = pd.to_numeric(df["previsto"], errors="coerce").fillna(0)
df["concluido"] = pd.to_numeric(df["concluido"], errors="coerce").fillna(0)

# Criar path da hierarquia para AgGrid (como lista)
df["hierarchy_path"] = df["hierarquia"].astype(str).apply(lambda x: x.split("."))

# Criar barra visual com blocos
def gerar_barra(val, largura=20):
    try:
        val = float(val)
    except:
        val = 0
    blocos = int(val * largura)
    return "█" * blocos + " " * (largura - blocos)

df["barra_concluido"] = df["concluido"].apply(gerar_barra)

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
    groupDefaultExpanded=0,
    getDataPath=JsCode("function(data) { return data.hierarchy_path; }")
)

# Esconder colunas auxiliares
gb.configure_columns(["hierarquia", "hierarchy_path"], hide=True)

# Configurar colunas principais
gb.configure_column("tarefa", header_name="Tarefa", flex=2)

gb.configure_column("previsto",
    header_name="% Previsto",
    cellStyle={"textAlign": "center"},
    type=["numericColumn"],
    maxWidth=120,
    valueFormatter=JsCode("function(params) { return (params.value).toFixed(1) + '%' }")
)

gb.configure_column("concluido",
    header_name="% Concluído",
    cellStyle={"textAlign": "center"},
    type=["numericColumn"],
    maxWidth=120,
    valueFormatter=JsCode("function(params) { return (params.value * 100).toFixed(1) + '%' }")
)

# 👉 Nova coluna visual com barra
gb.configure_column("barra_concluido",
    header_name="Barra de %",
    cellStyle={"fontFamily": "monospace", "textAlign": "left"},
    maxWidth=200
)

gb.configure_column("responsavel 1", header_name="Responsável 1", cellStyle={"textAlign": "center"}, maxWidth=160)
gb.configure_column("responsavel 2", header_name="Responsável 2", cellStyle={"textAlign": "center"}, maxWidth=160)
gb.configure_column("nome dos recursos", header_name="Recurso", cellStyle={"textAlign": "center"}, maxWidth=160)

# Exibir grid
AgGrid(
    df,
    gridOptions=gb.build(),
    height=450,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=True,
    fit_columns_on_grid_load=True
)
