import streamlit as st
from users import authenticate_user

st.set_page_config(page_title="Início", layout="centered", initial_sidebar_state="collapsed")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Login")

    username = st.text_input("Email")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        user_data = authenticate_user(username, password)
        if user_data:
            st.session_state.authenticated = True
            st.session_state.username = user_data["username"]
            st.session_state.role = user_data["role"]
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")


if "authenticated" not in st.session_state or not st.session_state.authenticated:
    hide_sidebar = """
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """
    st.markdown(hide_sidebar, unsafe_allow_html=True)

# Tela principal após login
if st.session_state.authenticated:
    # Exibe sidebar agora que está logado
    st.sidebar.title("Bem-vindo")
    st.sidebar.write(f"Usuário: {st.session_state.username}")
    st.sidebar.write(f"Permissão: {st.session_state.role}")

    if st.sidebar.button("Sair"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    # CSS e layout
    st.markdown("""
        <style>
            .stApp {
                background-color: black;
                background-image: none;
            }
        </style>
    """, unsafe_allow_html=True)

    st.image("logo-quanta-oficial.png", width=300)
    st.markdown("""
        <h1 style='color: white;'>Contratos - 25/2024-SEMINF</h1>
    """, unsafe_allow_html=True)

    colimg1, colimg2 = st.columns(2)
    with colimg1:
        st.image("prefeitura-macae.png", width=200)
    with colimg2:
        st.image("prefeitura-maricá.png", width=200)

    st.markdown("##")