import streamlit as st
import pandas as pd
from component_table_marica import mostrar_tabela
from component_graphbar_marica import mostrar_grafico
from component_graphbar_tasks_delay import mostrar_graficos_tarefas_atrasadas
import streamlit.components.v1 as components
from users import get_all_users_for_auth
from dotenv import load_dotenv
import os
import streamlit_authenticator as stauth

load_dotenv()

cookie_secret = os.getenv("KEY_COOKIE")

credentials = get_all_users_for_auth()

if credentials is None or len(credentials) == 0:
    st.error("Erro ao carregar usuários para autenticação. Tente novamente mais tarde.")
    st.stop()

authenticator = stauth.Authenticate(
    credentials={"usernames": credentials},
    cookie_name="meu_login_cookie",
    cookie_key=cookie_secret,
    cookie_expiry_days=7
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

authenticator.logout("Sair", "sidebar")
st.sidebar.success(f"👋 Bem-vindo(a), {name}")
# Exibir permissão
user_role = credentials[username]["role"]
st.sidebar.info(f"🔐 Permissão: {user_role}")

# =========================
# Carregar dados
# =========================
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
#df["barra_concluido"] = df["concluido"].apply(lambda val: "█" * int(float(val) * 20) + " " * (20 - int(float(val) * 20)))
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
st.set_page_config(page_title="Dashboard Maricá", layout="wide")

st.markdown("""
    <style>
        html, body, .stApp {
            padding-top: 0px !important;
            margin-top: 0px !important;
        }

        /* Opcional: reduz ainda mais o espaço do container principal */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 5px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Acompanhamento Geral Maricá")

col1, col2, col3 =  st.columns([0.03, 0.03, 0.2])

#with col1:
 #   if st.button("Voltar ao Início"):
 #       st.switch_page("dashboard.py") 

#with col2:
   # if st.button("Contrato Macaé"):
    #    st.switch_page("pages/macae_dashboard.py") 

# =========================
# Abas de navegação
# =========================
aba_tabela, aba_atrasadas = st.tabs(["📋 Tabela", "🚨 Atrasos Por Área"])

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

    def expandir_e_scrollar():
        st.session_state.mostrar_grafico = True
        st.session_state.scroll_to_graph = True

    col1, col2, col3, _ = st.columns([0.16, 0.15, 0.15, 0.70])
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