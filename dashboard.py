import streamlit as st
import streamlit_authenticator as stauth
from users import get_all_users_for_auth
from dotenv import load_dotenv
import os

load_dotenv()

cookie_secret = os.getenv("KEY_COOKIE")

# Configurar a página
st.set_page_config(page_title="Início", layout="wide", initial_sidebar_state="collapsed")

# Buscar usuários do banco
credentials = get_all_users_for_auth()

if credentials is None:
    st.error("❌ Erro ao conectar ao banco. Tente novamente.")
    st.stop()

# Criar config dinâmico
config = {
    "credentials": {
        "usernames": credentials
    },
    "cookie": {
        "expiry_days": 7,
        "key": cookie_secret,  # Altere para uma chave forte e secreta
        "name": "meu_login_cookie"
    }
}

# Autenticação
authenticator = stauth.Authenticate(
    credentials=config["credentials"],
    cookie_name=config["cookie"]["name"],
    cookie_key=config["cookie"]["key"],
    cookie_expiry_days=config["cookie"]["expiry_days"]
)

# Login (sem o segundo parâmetro 'location', que foi removido nas versões mais recentes)
name, authentication_status, username = authenticator.login("main", "Login")

# Verificar autenticação
if authentication_status:
    user_info = credentials[username]
    role = user_info["role"]

    authenticator.logout("Sair","sidebar") 
    st.sidebar.success(f"👋 Bem-vindo(a), {name}")
    st.sidebar.info(f"🔐 Permissão: {role}")

    # Conteúdo principal do dashboard
    st.image("logo-quanta-oficial.png", width=300)
    st.markdown("<h1 style='color: white;'>Contratos - 25/2024-SEMINF</h1>", unsafe_allow_html=True)

    colimg1, colimg2 = st.columns(2)
    with colimg1:
        st.image("prefeitura-macae.png", width=200)
    with colimg2:
        st.image("prefeitura-maricá.png", width=200)

    st.markdown("##")

    if role == "admin":
        st.success("🔧 Acesso administrativo concedido.")
        # Adicione aqui funcionalidades exclusivas para admin
    else:
        st.info("👤 Usuário comum - acesso limitado.")

elif authentication_status is False:
    st.error("Usuário ou senha incorretos.")

elif authentication_status is None:
    st.warning("Informe suas credenciais para continuar.")
