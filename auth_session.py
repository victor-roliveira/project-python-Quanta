import streamlit as st
import streamlit_authenticator as stauth
from users import get_all_users_for_auth
from dotenv import load_dotenv
import os

load_dotenv()
cookie_secret = os.getenv("KEY_COOKIE")

def get_authenticator():
    credentials = get_all_users_for_auth()
    if not credentials:
        st.error("❌ Erro ao acessar o banco de dados.")
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
    authenticator, credentials = get_authenticator()
    name, auth_status, username = authenticator.login("main", "Login")

    if auth_status is None:
        st.warning("Informe suas credenciais para continuar.")
        return None

    if auth_status is False:
        st.error("Usuário ou senha incorretos.")
        return None

    if auth_status:
        with st.sidebar:
            authenticator.logout("Sair", "sidebar")
            # Aplica estilo ao botão de logout
            # Estilo para aumentar o botão "Sair"
            st.markdown("""
            <style>
            button[data-testid="stBaseButton-secondary"] div p {
                font-size: 20px !important;
            }

            button[data-testid="stBaseButton-secondary"] {
                padding: 5px 20px  !important;
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

# ✅ Para outras páginas (sem login, só verificação)
def check_authentication_only():
    authenticator, credentials = get_authenticator()

    # Condições de não-autenticação seguras
    if (
        st.session_state.get("authentication_status") != True
        or "username" not in st.session_state
        or "name" not in st.session_state
    ):
        st.image("acesso-negado.jpg", use_container_width=True)
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


