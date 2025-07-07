import streamlit as st

st.set_page_config(page_title="Início", layout="centered")

st.image("logo-quanta-oficial.png", width=300)
st.title("Selecione um contrato")
st.markdown("##")

col1, col2 = st.columns(2)

with col1:
    if st.button("Contrato Macaé"):
        st.switch_page("pages/macae_dashboard.py")

with col2:
    if st.button("Contrato Maricá"):
        st.switch_page("pages/marica_dashboard.py")
