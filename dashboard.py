import streamlit as st
from auth_session import login_user

session_data = login_user()
if not session_data:
    st.stop()

# Configurar a página
st.set_page_config(page_title="Início", layout="centered", initial_sidebar_state="collapsed")

# Conteúdo principal do dashboard
st.image("logo-quanta-oficial.png", width=300)
st.markdown("<h1 style='color: white;'>Contratos - 25/2024-SEMINF</h1>", unsafe_allow_html=True)

colimg1, colimg2 = st.columns(2)

with colimg1:
    st.image("prefeitura-macae.png", width=200)
with colimg2:
    st.image("prefeitura-maricá.png", width=200)

st.markdown("##")

if session_data["role"] == "admin":
    st.success("🔧 Acesso administrativo")