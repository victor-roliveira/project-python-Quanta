import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# =========================
# Carregar a planilha
# =========================
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

# Hierarquia como lista
df["hierarchy_path"] = df["hierarquia"].astype(str).apply(lambda x: x.split("."))

# Barra visual com blocos
def gerar_barra(val, largura=20):
    try:
        val = float(val)
    except:
        val = 0
    blocos = int(val * largura)
    return "█" * blocos + " " * (largura - blocos)

df["barra_concluido"] = df["concluido"].apply(gerar_barra)

# Reordenar colunas para exibir a barra após a % concluído
colunas = list(df.columns)
idx = colunas.index("concluido")
colunas.remove("barra_concluido")
colunas.insert(idx + 1, "barra_concluido")
df = df[colunas]

# =========================
# Streamlit layout
# =========================
st.set_page_config(page_title="Dashboard com Hierarquia", layout="wide")
st.title("📊 Acompanhamento Geral Macaé")
st.markdown("Explore o andamento das tarefas.")

# =========================
# AGGRID - TABELA PRINCIPAL
# =========================
gb = GridOptionsBuilder.from_dataframe(df)

gb.configure_grid_options(
    treeData=True,
    animateRows=True,
    groupDefaultExpanded=0,
    getDataPath=JsCode("function(data) { return data.hierarchy_path; }")
)

gb.configure_columns(["hierarquia", "hierarchy_path"], hide=True)

gb.configure_column("tarefa", header_name="Tarefa", headerStyle={"textAlign": "center"}, flex=2)

gb.configure_column("previsto",
    header_name="% Previsto",
    headerStyle={"textAlign": "center"},
    cellStyle={"textAlign": "center"},
    type=["numericColumn"],
    maxWidth=120,
    valueFormatter=JsCode("function(params) { return (params.value).toFixed(2) + '%' }")
)

gb.configure_column("concluido",
    header_name="% Concluído",
    headerStyle={"textAlign": "center"},
    cellStyle={"textAlign": "center"},
    type=["numericColumn"],
    maxWidth=120,
    valueFormatter=JsCode("function(params) { return (params.value * 100).toFixed(2) + '%' }")
)

gb.configure_column("barra_concluido",
    header_name="Barra de %",
    headerStyle={"textAlign": "center"},
    cellStyle={"fontFamily": "monospace", "textAlign": "left"},
    maxWidth=180
)

gb.configure_column("responsavel 1", header_name="AT 1", cellStyle={"textAlign": "center"}, maxWidth=120)
gb.configure_column("responsavel 2", header_name="AT 2", cellStyle={"textAlign": "center"}, maxWidth=120)
gb.configure_column("nome dos recursos", header_name="Recurso", headerStyle={"textAlign": "center"}, cellStyle={"textAlign": "center"}, maxWidth=140)

AgGrid(
    df,
    gridOptions=gb.build(),
    height=450,
    allow_unsafe_jscode=True,
    enable_enterprise_modules=True,
    fit_columns_on_grid_load=True,
    custom_css={
        "#agridToolBar":{
            "font-size": "18px"
        },
        ".ag-cell": { 
            "font-size": "16px",
            "line-height": "22px"
        },
        ".ag-header-cell-text": {
            "font-size": "12px",
        },
        ".ag-header-cell-label": {
            "justify-content": "center",  
            "align-items": "center"        
        },
    }
)

# =========================
# GRÁFICO AGRUPADO
# =========================

# Extrair tópicos principais e subtópicos
df["topico_nivel1"] = df["hierarquia"].astype(str).str.split(".").str[0].str.strip()
df["topico_nivel2"] = df["hierarquia"].astype(str).apply(lambda x: ".".join(x.split(".")[:2]) if len(x.split(".")) > 1 else x).str.strip()

# Criar lista para filtro
opcoes_filtro = ["Todos os Tópicos"]

topicos1_ord = sorted(df["topico_nivel1"].unique(), key=lambda x: int(x) if x.isdigit() else x)
for t1 in topicos1_ord:
    nome_t1 = df[df["topico_nivel1"] == t1]["tarefa"].iloc[0]
    opcoes_filtro.append(f"{t1} - {nome_t1}")
    
    subtopicos = sorted(df[df["topico_nivel1"] == t1]["topico_nivel2"].unique(), key=lambda x: [int(i) if i.isdigit() else i for i in x.split(".")])
    for stp in subtopicos:
        if stp != t1:
            nome_stp = df[df["topico_nivel2"] == stp]["tarefa"].iloc[0]
            opcoes_filtro.append(f"  {stp} - {nome_stp}")

# 🎯 MOVER FILTRO PARA SIDEBAR
selecao = st.sidebar.selectbox("Filtro de Tarefas", opcoes_filtro, index=0)

# Obter o código selecionado
if selecao == "Todos os Tópicos":
    selecao_valor = "Default"
else:
    selecao_valor = selecao.strip().split(" ")[0]

# Padronizar campos
df["topico_nivel1"] = df["topico_nivel1"].astype(str).str.strip()
df["topico_nivel2"] = df["topico_nivel2"].astype(str).str.strip()

# Filtrar dados para o gráfico
if selecao_valor == "Default":
    df_plot = df[df["topico_nivel1"].isin(["1", "2", "3", "4", "5", "6"])].copy()
else:
    df_plot = df[df["hierarquia"].astype(str).str.startswith(selecao_valor + ".") | (df["hierarquia"].astype(str) == selecao_valor)].copy()

# Garantir escala 0-100
if df_plot["previsto"].max() <= 1:
    df_plot["previsto"] *= 100
if df_plot["concluido"].max() <= 1:
    df_plot["concluido"] *= 100

# Exibir gráfico
st.markdown("---")
st.subheader("📊 Comparativo de Tarefas")

fig = px.bar(
    df_plot,
    x="tarefa",
    y=["previsto", "concluido"],
    labels={"value": "Percentual", "variable": "Tipo", "tarefa": "Tarefa"},
    barmode="group",
    height=500,
    color_discrete_map={
        "previsto": "#f08224",
        "concluido": "#ffffff"
    }
)

fig.update_layout(
    yaxis=dict(range=[0, 100], tickformat=".2f", title="Percentual (%)"),
    xaxis_title="Tarefa",
    legend_title=""
)

fig.update_xaxes(tickangle=-45)
st.plotly_chart(fig, use_container_width=True)
