import streamlit as st
import pandas as pd
from component_table import mostrar_tabela
from component_graphbar import mostrar_grafico
from component_graphbar_tasks_delay import mostrar_graficos_tarefas_atrasadas
from auth_session import protect_page

st.set_page_config(page_title="Dashboard Macaé", page_icon="icone-quanta.png",layout="wide")
st.logo("logo-quanta-oficial.png", size="large")

# --- Autenticação centralizada ---
protect_page()
# --- Estilos ---
st.markdown("""
    <style>
        html, body, .stApp {
            padding-top: 0px !important;
            margin-top: 0px !important;
        }
        .block-container {
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }
    </style>
""", unsafe_allow_html=True)
# --- Carregar dados ---
df = pd.read_excel("ProjectEmExcel_MKE.xlsx")

df = df[[ 
    "Número Hierárquico", "Nome da Tarefa", "Término",
    "%concluida prev. (Número10)", "% Concluída",
    "Responsável 01", "Responsável 02", "Nomes de Recursos", "Exe."
]].copy()

df.columns = [
    "hierarquia", "tarefa", "termino", "previsto", "concluido",
    "responsavel 1", "responsavel 2", "nome dos recursos", "execucao"
]
df["previsto"] = pd.to_numeric(df["previsto"], errors="coerce").fillna(0)
df["concluido"] = pd.to_numeric(df["concluido"], errors="coerce").fillna(0)
df["hierarchy_path"] = df["hierarquia"].astype(str).apply(lambda x: x.split("."))

df["barra_info"] = df.apply(lambda row: {
    "concluido": round(row["concluido"] * 100),
    "previsto": round(row["previsto"])
}, axis=1).apply(lambda x: str(x).replace("'", '"'))

colunas = list(df.columns)
idx = colunas.index("concluido")
colunas.remove("barra_info")
colunas.insert(idx + 1, "barra_info")
df = df[colunas]

st.title("Acompanhamento Geral Macaé")

aba_tabela, aba_atrasadas, aba_resumo = st.tabs(["📋 Tabela", "🚨 Atrasos Por Área", "ℹ️ Avanço Geral"])

with aba_tabela:
    if "selecao_tabela" not in st.session_state:
        st.session_state.selecao_tabela = None
    if "limpar_selecao_tabela" not in st.session_state:
        st.session_state.limpar_selecao_tabela = False

    limpar = st.session_state.limpar_selecao_tabela
    linha_selecionada = mostrar_tabela(df.drop(columns=["execucao"]), limpar_selecao=limpar)

    if limpar:
        st.session_state.limpar_selecao_tabela = False

    if linha_selecionada == 0:
        st.session_state.selecao_tabela = None
    elif linha_selecionada:
        st.session_state.selecao_tabela = linha_selecionada

    selecao_valor = st.session_state.get("selecao_tabela")
    selecao_valor = selecao_valor if selecao_valor else "Todos"
    mostrar_grafico(df, str(selecao_valor))

with aba_atrasadas:
    mostrar_graficos_tarefas_atrasadas(df)

with aba_resumo:
    st.markdown("<h3 style='text-align: center;'>Resumo Geral de Avanço</h3>", unsafe_allow_html=True)
    st.image("resumo_geral.png", use_container_width=True, output_format="PNG")
