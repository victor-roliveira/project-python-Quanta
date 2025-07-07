import streamlit as st

st.set_page_config(page_title="Início", layout="centered")

# ✅ CSS para fundo e botões
st.markdown("""
<style>
    .stApp {
        background-color: #3c3c3b;
        background-image: none;
    }

    div.stButton > button {
        background-color: #FF5733;  
        color: white;               
        border-radius: 10px;
        height: 3em;
        font-weight: bold;
    }
    div.stButton > button:hover {
        background-color: #C70039;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ✅ Logomarca
st.image("logo-quanta-oficial.png", width=300)

# ✅ Título estilizado com HTML
st.markdown("""
    <h1 style='color: white;'>Contratos - 25/2024-SEMINF</h1>
""", unsafe_allow_html=True)

# ✅ Imagens das prefeituras lado a lado
colimg1, colimg2 = st.columns(2)
with colimg1:
    st.image("prefeitura-macae.png", width=200)
with colimg2:
    st.image("prefeitura-maricá.png", width=200)

st.markdown("##")

# ✅ Botões lado a lado
col1, col2 = st.columns(2)

with col1:
    if st.button("Assessoria e Projetos SEMED"):
        st.switch_page("pages/macae_dashboard.py")

with col2:
    if st.button("Assessoria Codemar"):
        st.switch_page("pages/marica_dashboard.py")
