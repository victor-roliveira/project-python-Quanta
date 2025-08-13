import streamlit as st
import streamlit_authenticator as stauth
from users import get_all_users_for_auth
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente
load_dotenv()
COOKIE_SECRET = os.getenv("KEY_COOKIE")

def initialize_authenticator():
    """
    Cria e inicializa o objeto Authenticator, armazenando-o no st.session_state
    para que seja persistente entre as páginas.
    """
    if "authenticator" in st.session_state:
        return st.session_state["authenticator"]

    try:
        # A função get_all_users_for_auth() retorna apenas o dicionário de usuários
        user_credentials = get_all_users_for_auth()
        if not user_credentials:
            st.error("Erro: Nenhuma credencial encontrada no banco de dados.")
            st.stop()
    except Exception as e:
        st.error(f"Erro ao acessar o banco de dados para autenticação: {e}")
        st.stop()
    
    # --- CORREÇÃO APLICADA AQUI ---
    # Criamos o dicionário no formato que a biblioteca espera,
    # envolvendo os dados dos usuários com a chave 'usernames'.
    credentials_for_auth = {"usernames": user_credentials}

    authenticator = stauth.Authenticate(
        credentials_for_auth, # Passamos o dicionário no formato correto
        "meu_app_cookie",
        COOKIE_SECRET,
        7
    )

    # Armazena o objeto no session_state
    st.session_state["authenticator"] = authenticator
    # Armazenamos os dados originais dos usuários para acesso posterior (ex: role)
    st.session_state["credentials"] = user_credentials
    
    return authenticator

def display_error_page():
    """Exibe uma página de erro padrão para acesso não autorizado."""
    st.markdown("""
    <div style='text-align: center; font-size: 60px;'>⚠️</div>
    <div style='text-align: center; font-size: 20px; margin-top: 10px;'>
        <strong>Acesso Negado</strong><br>
        Você não está logado ou não tem permissão para acessar essa página.
    </div>
    <div style='display: flex; justify-content: center; margin-top: 30px;'>
        <a href="/" target="_self">
            <button style='
                padding: 10px 25px; font-size: 18px; background-color: #f63366;
                color: white; border: none; border-radius: 8px; cursor: pointer;'>
                Ir para a tela de Login
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)

def render_logout_button():
    """Renderiza o botão de logout na sidebar."""
    authenticator = st.session_state.get("authenticator")
    if authenticator and st.session_state.get("authentication_status"):
        with st.sidebar:
            st.success(f"Bem-vindo(a), {st.session_state.get('name', '')}")
            authenticator.logout("Sair", "sidebar")
            st.markdown("""
            <style>
            button[data-testid="stBaseButton-secondary"] div p {
                font-size: 20px !important;
            }

            button[data-testid="stBaseButton-secondary"] {
                padding: 5px 20px !important;
                background-color: orange !important;
                color: white !important;
                border-radius: 8px !important;
                border: none !important;
                width: 218px;
            }
            </style>
            """, unsafe_allow_html=True)

def run_login_page():
    authenticator = initialize_authenticator()
    authenticator.login()

    if st.session_state.get("authentication_status"):
        render_logout_button()
        return True
    elif st.session_state.get("authentication_status") is False:
        st.error("Usuário ou senha incorretos.")
        return False
    elif st.session_state.get("authentication_status") is None:
        st.warning("Por favor, informe seu usuário e senha.")
        return False
    return False

def protect_page():
    """
    Protege uma página, verificando se o usuário está logado.
    """
    if "authenticator" not in st.session_state:
        initialize_authenticator()

    if not st.session_state.get("authentication_status"):
        display_error_page()
        st.stop()
    
    render_logout_button()