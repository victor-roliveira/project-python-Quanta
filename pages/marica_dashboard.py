import streamlit as st
import pandas as pd
from component_table_marica import mostrar_tabela
from component_graphbar_marica import mostrar_grafico
from component_graphbar_tasks_marica import mostrar_graficos_tarefas_atrasadas
import streamlit.components.v1 as components
from auth_session import check_authentication_only

session_data = check_authentication_only()

# Carregar dados
df = pd.read_excel("013A.xlsx")

df = df[[
    "D - N° Guia", "E - Nome Da Tarefa", "H - Conclusão",
    "% Ideal", "C - % Concluída",
    "K - Responsável", "L - Recurso", "B - Status"
]].copy()

df.columns = [
    "hierarquia", "tarefa", "conclusao", "previsto", "concluido",
    "responsavel 1", "responsavel 2", "execucao"
]

df["previsto"] = pd.to_numeric(df["previsto"], errors="coerce").fillna(0)
df["concluido"] = pd.to_numeric(df["concluido"], errors="coerce").fillna(0)
df["hierarchy_path"] = df["hierarquia"].astype(str).apply(lambda x: x.split("."))
df["barra_info"] = df.apply(lambda row: {
    "concluido": round(row["concluido"] * 100),
    "previsto": round(row["previsto"])
}, axis=1).apply(lambda x: str(x).replace("'", '"'))
# Reordenar colunas (opcional)
colunas = list(df.columns)
idx = colunas.index("concluido")
colunas.remove("barra_info") 
colunas.insert(idx + 1, "barra_info")
df = df[colunas]

# =========================
# Layout
# =========================
st.set_page_config(page_title="Dashboard Maricá", page_icon="icone-quanta.png",layout="wide")
st.logo("logo-quanta-oficial.png", size="large")

st.markdown("""
    <style>
        html, body, .stApp {
            padding-top: 0px !important;
            margin-top: 0px !important;
        }

        /* Opcional: reduz ainda mais o espaço do container principal */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Acompanhamento Geral Maricá")

col1, col2, col3 =  st.columns([0.03, 0.03, 0.2])

# Abas de navegação
aba_tabela, aba_atrasadas = st.tabs(["📋 Tabela", "🚨 Atrasos Por Área"])

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