import streamlit as st
from auth_session import run_login_page
import base64
from pathlib import Path

# --- Configuração da Página ---
st.set_page_config(
    page_title="Início",
    page_icon="icone-quanta.png",
    layout="centered",
    initial_sidebar_state="auto"
)

st.logo("logo-quanta-oficial.png", size="large")

# A função de conversão da imagem continua a mesma
def imagem_para_base64(caminho_para_imagem: str) -> str:
    """Lê uma imagem e a converte para uma string Base64."""
    try:
        with open(caminho_para_imagem, "rb") as f:
            dados = f.read()
        return base64.b64encode(dados).decode()
    except FileNotFoundError:
        return ""

# --- Autenticação ---
is_logged_in = run_login_page()

# --- Se o login tiver sucesso, exibe o conteúdo do dashboard ---
if is_logged_in:
    
    st.markdown("<h1 style='color: white;'>Contratos - 25/2024-SEMINF</h1>", unsafe_allow_html=True)

    # --- NAVEGAÇÃO COM BOTÕES (A FORMA CORRETA) ---

    colimg1, colimg2 = st.columns(2)

    with colimg1:
        st.image("prefeitura-macae.png", width=200)
        # O botão aciona a função st.switch_page, que navega sem perder a sessão
        if st.button("Assessoria SEMED", key="btn_macae"):
            st.switch_page("pages/macae_dashboard.py")

    with colimg2:
        st.image("prefeitura-maricá.png", width=200)
        if st.button("Assessoria CODEMAR", key="btn_marica"):
            st.switch_page("pages/marica_dashboard.py")

    st.divider()

    # Acessando a permissão (role) de forma segura a partir do st.session_state
    credentials = st.session_state.get("credentials", {})
    username = st.session_state.get("username")
    user_data = credentials.get(username, {})
    role = user_data.get("role", "comum")

    if role == "admin":
        st.markdown(":orange[:material/crown: Acesso como Administrador]")