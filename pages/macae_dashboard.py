import streamlit as st
import pandas as pd
from component_table import mostrar_tabela
from component_graphbar import mostrar_grafico
from component_graphbar_tasks_delay import mostrar_graficos_tarefas_atrasadas
from auth_session import check_authentication_only

st.set_page_config(page_title="Dashboard Macaé", layout="wide")

# --- Autenticação centralizada ---
session_data = check_authentication_only()

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

## Função para Carregar e Processar Dados (com Cache)
@st.cache_data(show_spinner="Carregando e processando dados...")
def carregar_e_processar_dados(caminho_arquivo: str) -> pd.DataFrame:
    """
    Carrega a planilha do Excel e realiza o pré-processamento inicial dos dados.
    O resultado desta função é cacheado pelo Streamlit.
    """
    df = pd.read_excel(caminho_arquivo)

    # Seleção e renomeação de colunas
    df = df[[
        "Número Hierárquico", "Nome da Tarefa", "Término",
        "%concluida prev. (Número10)", "% Concluída",
        "Responsável 01", "Responsável 02", "Nomes de Recursos", "Exe."
    ]].copy()

    df.columns = [
        "hierarquia", "tarefa", "termino", "previsto", "concluido",
        "responsavel 1", "responsavel 2", "nome dos recursos", "execucao"
    ]

    # Conversão de tipos e preenchimento de NaNs
    df["previsto"] = pd.to_numeric(df["previsto"], errors="coerce").fillna(0)
    df["concluido"] = pd.to_numeric(df["concluido"], errors="coerce").fillna(0)

    # Criação da coluna hierarchy_path
    df["hierarchy_path"] = df["hierarquia"].astype(str).apply(lambda x: x.split("."))

    # Preparação da coluna 'barra_info' no formato JSON string
    # É crucial que esta coluna seja preparada aqui, antes de ser passada para as componentes
    # pois o JsCode da tabela espera a string JSON.
    df["barra_info_data"] = df.apply(lambda row: {
        "concluido": round(row["concluido"] * 100),
        "previsto": round(row["previsto"])
    }, axis=1).apply(lambda x: str(x).replace("'", '"'))

    return df

# --- Carregar dados (Chamando a função cacheada) ---
df_principal = carregar_e_processar_dados("ProjectEmExcel_MKE.xlsx")

# --- Interface do Usuário ---
st.title("Acompanhamento Geral Macaé")

aba_tabela, aba_atrasadas, aba_resumo = st.tabs(["📋 Tabela", "🚨 Atrasos Por Área", "ℹ️ Avanço Geral"])

with aba_tabela:
    if "selecao_tabela" not in st.session_state:
        st.session_state.selecao_tabela = None
    if "limpar_selecao_tabela" not in st.session_state:
        st.session_state.limpar_selecao_tabela = False

    limpar = st.session_state.limpar_selecao_tabela

    linha_selecionada = mostrar_tabela(df_principal.drop(columns=["execucao"]), limpar_selecao=limpar)

    if limpar:
        st.session_state.limpar_selecao_tabela = False

    if linha_selecionada == 0:
        st.session_state.selecao_tabela = None
    elif linha_selecionada:
        st.session_state.selecao_tabela = linha_selecionada

    selecao_valor = st.session_state.get("selecao_tabela")
    selecao_valor = selecao_valor if selecao_valor else "Todos"

    mostrar_grafico(df_principal, str(selecao_valor))

with aba_atrasadas:
    mostrar_graficos_tarefas_atrasadas(df_principal)

with aba_resumo:
    st.markdown("<h3 style='text-align: center;'>Resumo Geral de Avanço</h3>", unsafe_allow_html=True)
    st.image("resumo_geral.png", use_container_width=True, output_format="PNG")