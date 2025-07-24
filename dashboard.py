import streamlit as st
from auth_session import login_user

session_data = login_user()
if not session_data:
    st.stop()

# Configurar a página
st.set_page_config(page_title="Início", page_icon="icone-quanta.png", layout="centered")

# Conteúdo principal do dashboard
st.logo("logo-quanta-oficial.png", size="large")
st.markdown("<h1 style='color: white;'>Contratos - 25/2024-SEMINF</h1>", unsafe_allow_html=True)

colimg1, colimg2 = st.columns(2)

with colimg1:
    st.image("prefeitura-macae.png", width=200)
with colimg2:
    st.image("prefeitura-maricá.png", width=200)

st.divider()

if session_data["role"] == "admin":
    st.markdown(
    ":orange[:material/crown: Acesso como Administrador]"
)
