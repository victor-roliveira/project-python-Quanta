import streamlit as st
import pandas as pd
import streamlit_authenticator as stauth
import streamlit.components.v1 as components
from users import get_all_users_for_auth
from component_table import mostrar_tabela
from component_graphbar import mostrar_grafico
from component_graphbar_tasks_delay import mostrar_graficos_tarefas_atrasadas
from dotenv import load_dotenv
import os

load_dotenv()

cookie_secret = os.getenv("KEY_COOKIE")

st.set_page_config(page_title="Dashboard Macaé", layout="centered")

# --- Buscar credenciais do banco ---
credentials = get_all_users_for_auth()

if credentials is None or len(credentials) == 0:
    st.error("❌ Erro ao carregar usuários para autenticação. Tente novamente mais tarde.")
    st.stop()

# --- Configuração do authenticator ---
authenticator = stauth.Authenticate(
    credentials={"usernames": credentials},
    cookie_name="meu_login_cookie",
    cookie_key=cookie_secret, 
    cookie_expiry_days=7,
)

# --- Verificar autenticação ---
if "authentication_status" not in st.session_state:
    # Mostrar apenas o formulário de login, nada mais
    name, authentication_status, username = authenticator.login("Login", "main")
    
    if authentication_status != True:
        # Mostrar apenas imagem
        st.image("acesso-negado.jpg", use_container_width=True)
        st.stop()

    # Se autenticado, salvar dados na sessão
    st.session_state.authentication_status = authentication_status
    st.session_state.name = name
    st.session_state.username = username

# Recuperar dados da sessão
authentication_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")
username = st.session_state.get("username")

# Verificar se realmente está autenticado
if authentication_status != True:
    st.image("acesso-negado.jpg", use_container_width=True)
    st.stop()

# Usuário autenticado
authenticator.logout("Sair", "sidebar")
st.sidebar.success(f"👋 Bem-vindo(a), {name}")

# Exibir permissão
user_role = credentials[username]["role"]
st.sidebar.info(f"🔐 Permissão: {user_role}")

# --- Estilos ---
st.markdown("""
    <style>
        html, body, .stApp {
            padding-top: 0px !important;
            margin-top: 0px !important;
        }
        .block-container {
            padding-top: 20px !important;
            padding-bottom: 5px !important;
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
    if "mostrar_grafico" not in st.session_state:
        st.session_state.mostrar_grafico = False
    if "scroll_to_graph" not in st.session_state:
        st.session_state.scroll_to_graph = False
    if "selecao_tabela" not in st.session_state:
        st.session_state.selecao_tabela = None
    if "limpar_selecao_tabela" not in st.session_state:
        st.session_state.limpar_selecao_tabela = False

    limpar = st.session_state.limpar_selecao_tabela
    linha_selecionada = mostrar_tabela(df.drop(columns=["execucao"]), limpar_selecao=limpar)

    if limpar:
        st.session_state.limpar_selecao_tabela = False

    if linha_selecionada:
        st.session_state.selecao_tabela = linha_selecionada

    if linha_selecionada == 0:
        st.session_state.selecao_tabela = None

    def expandir_e_scrollar():
        st.session_state.mostrar_grafico = True
        st.session_state.scroll_to_graph = True

    col1, col2, col3, _ = st.columns([0.15, 0.15, 0.15, 0.70])
    with col1:
        st.button(
            "📊 Visualizar Gráfico",
            key="btn_expandir",
            disabled=st.session_state.mostrar_grafico,
            on_click=expandir_e_scrollar
        )
    with col2:
        st.button(
            "🔼 Recolher Gráfico",
            key="btn_recolher",
            disabled=not st.session_state.mostrar_grafico,
            on_click=lambda: st.session_state.update({"mostrar_grafico": False})
        )
    with col3:
        if st.button("🔄 Limpar Filtro"):
            st.session_state.selecao_tabela = None
            st.session_state.limpar_selecao_tabela = True
            st.success("Filtro limpo! Exibindo projetos principais.")

    st.markdown("")

    if st.session_state.mostrar_grafico:
        st.markdown('<div id="grafico-anchor"></div>', unsafe_allow_html=True)

        selecao_valor = st.session_state.get("selecao_tabela")
        selecao_valor = selecao_valor if selecao_valor else "Todos"

        mostrar_grafico(df, str(selecao_valor))

        if st.session_state.scroll_to_graph:
            components.html(
                """
                <script>
                    const anchor = window.parent.document.getElementById("grafico-anchor");
                    if(anchor){
                        anchor.scrollIntoView({ behavior: "smooth", block: "start" });
                    }
                </script>
                """,
                height=0
            )
            st.session_state.scroll_to_graph = False

with aba_atrasadas:
    mostrar_graficos_tarefas_atrasadas(df)

with aba_resumo:
    st.markdown("""
        <style>
            .resumo-img {
                height: 1200px;
                width: 100%;
                object-fit: cover;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center;'>Resumo Geral de Avanço</h3>", unsafe_allow_html=True)
    st.image("resumo_geral.png", use_container_width=True, output_format="PNG")
