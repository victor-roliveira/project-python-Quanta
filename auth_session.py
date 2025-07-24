import streamlit as st
import streamlit_authenticator as stauth
from users import get_all_users_for_auth
from dotenv import load_dotenv
import os

load_dotenv()
cookie_secret = os.getenv("KEY_COOKIE")

@st.cache_data(ttl=3600)
def get_credentials_cached():
    try:
        credentials = get_all_users_for_auth()
        if not credentials:
            st.error("Erro: nenhuma credencial encontrada.")
            st.markdown("""
            <div style='text-align: center; font-size: 60px;'>⚠️</div>
            <div style='text-align: center; font-size: 20px; margin-top: 10px;'>
                <strong>Alguma coisa deu errado</strong><br>
                Você não está logado ou não tem permissão para acessar essa página.
            </div>
            <div style='display: flex; justify-content: center; margin-top: 30px;'>
                <a href="/" target="_self">
                    <button style='
                        padding: 10px 25px;
                        font-size: 18px;
                        background-color: #f63366;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                    '>
                        Fazer login
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)
            st.stop()
            return None
        return credentials
    except Exception as e:
        st.error(f"Erro ao acessar o banco de dados: {e}")
        return None

def get_authenticator():
    credentials = get_credentials_cached()
    if credentials is None:
        st.stop()

    config = {
        "credentials": {
            "usernames": credentials
        },
        "cookie": {
            "expiry_days": 7,
            "key": cookie_secret,
            "name": "meu_login_cookie"
        }
    }

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"]
    )
    return authenticator, credentials

# ✅ Para a página inicial (login e dashboard)
def login_user():
    st.logo("logo-quanta-oficial.png", size="large")
    authenticator, credentials = get_authenticator()
    name, auth_status, username = authenticator.login("main", "Login")

    if credentials is None:
        st.error("Não foi possível carregar as credenciais.")
        st.stop()

    if auth_status is None:
        st.warning("Informe suas credenciais para continuar.")
        return None

    if auth_status is False:
        st.error("Usuário ou senha incorretos.")
        return None

    if auth_status:
        with st.sidebar:
            authenticator.logout("Sair", "sidebar")
            st.markdown("""
            <style>
            button[data-testid="stBaseButton-secondary"] div p {
                font-size: 20px !important;
            }

            button[data-testid="stBaseButton-secondary"] {
                padding: 5px 20px !important;
                background-color: #f63366 !important;
                color: white !important;
                border-radius: 8px !important;
                border: none !important;
                width: 218px;
            }
            </style>
            """, unsafe_allow_html=True)

            st.success(f"Bem-vindo(a), {name}")
            st.info(f"Permissão: {credentials[username]['role']}")
        return {
            "authenticated": True,
            "username": username,
            "name": name,
            "role": credentials[username]["role"]
        }

    if st.session_state.get("logout"):
        st.session_state.authentication_status = None
        st.session_state.username = None
        st.session_state.name = None

def check_authentication_only():
    authenticator, credentials = get_authenticator()

    if credentials is None:
        st.error("Não foi possível carregar as credenciais.")
        st.stop()
    if (
        st.session_state.get("authentication_status") != True
        or "username" not in st.session_state
        or "name" not in st.session_state
    ):
        st.markdown("""
        <div style='text-align: center; font-size: 60px;'>⚠️</div>
        <div style='text-align: center; font-size: 20px; margin-top: 10px;'>
            <strong>Alguma coisa deu errado</strong><br>
            Você não está logado ou não tem permissão para acessar essa página.
        </div>
        <div style='display: flex; justify-content: center; margin-top: 30px;'>
            <a href="/" target="_self">
                <button style='
                    padding: 10px 25px;
                    font-size: 18px;
                    background-color: #f63366;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                '>
                    Fazer login
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    username = st.session_state["username"]
    name = st.session_state["name"]
    role = credentials.get(username, {}).get("role", "comum")

    with st.sidebar:
        authenticator.logout("Sair", "sidebar")
        st.markdown("""
        <style>
        button[data-testid="stBaseButton-secondary"] div p {
            font-size: 20px !important;
        }

        button[data-testid="stBaseButton-secondary"] {
            padding: 5px 20px !important;
            background-color: #f63366 !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            width: 218px;
        }
        </style>
        """, unsafe_allow_html=True)
        st.success(f"Bem-vindo(a), {name}")
        st.info(f"Permissão: {role}")

    return {
        "authenticated": True,
        "username": username,
        "name": name,
        "role": role
    }
