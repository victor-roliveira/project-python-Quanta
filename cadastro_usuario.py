import streamlit as st
from users import create_user

st.set_page_config(page_title="Cadastro de Usuário", layout="centered")

st.title("👤 Cadastro de Novo Usuário")

# Entrada de dados
username = st.text_input("Nome de usuário")
password = st.text_input("Senha", type="password")
role = st.selectbox("Permissão do usuário", ["comum", "admin"])

# Botão de ação
if st.button("Cadastrar"):
    if not username or not password:
        st.warning("Por favor, preencha todos os campos.")
    else:
        try:
            create_user(username, password, role)
            st.success(f"Usuário '{username}' criado com sucesso com permissão '{role}'.")
        except Exception as e:
            st.error(f"Erro ao cadastrar usuário: {str(e)}")
