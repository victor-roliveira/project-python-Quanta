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

st.markdown("""
    <style>
        /* Torna a sidebar mais escura no tema claro */
        /* Seletor para o container principal da sidebar (ATUALIZADO) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 {
            background-color: #333333; /* Um cinza escuro para a sidebar */
            color: #FFFFFF; /* Cor do texto geral dentro da sidebar para contraste */
        }
        
        /* Estiliza o TEXTO dentro dos ITENS (páginas/links) da sidebar */
        /* Seletor do texto dos links da sidebar (ATUALIZADO com a nova classe do pai) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.e16b601d0 > ul > li > div > a > span {
            color: #ADD8E6 !important; /* Exemplo: Azul claro para o texto dos links */
        }

        /* Estiliza o HOVER (quando o mouse passa por cima) dos itens da sidebar */
        /* Seletor do hover dos links da sidebar (ATUALIZADO com a nova classe do pai) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.e16b601d0 > ul > li > div > a:hover {
            background-color: #555555; /* Um fundo levemente mais claro no hover */
            border-radius: 5px; /* Adiciona bordas arredondadas no hover */
        }
        /* Estiliza o texto do item no HOVER (ATUALIZADO com a nova classe do pai) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.e16b601d0 > ul > li > div > a:hover > span {
            color: #00BFFF !important; /* Um azul mais forte no hover para o texto */
        }

        /* Estiliza o item ATIVO (página atualmente selecionada) na sidebar */
        /* Seletor da página ativa na sidebar (ATUALIZADO com a nova classe do pai) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.e16b601d0 > ul > li > div > a[aria-current="page"] {
            background-color: #444444; /* Fundo diferente para a página ativa */
        }
        /* Estiliza o texto do item ATIVO (ATUALIZADO com a nova classe do pai) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.e16b601d0 > ul > li > div > a[aria-current="page"] > span {
            color: #FFD700 !important; /* Exemplo: Amarelo para a página ativa */
            font-weight: bold; /* Deixa o texto em negrito */
        }

        /* Ajuste para o logo, se estiver dentro da sidebar e precisar de ajuste */
        /* Seletor do logo (ATUALIZADO com a nova classe do pai) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 img {
            filter: brightness(0) invert(1); /* Inverte as cores da imagem (útil para logos pretos em fundo branco) */
        }

        /* Exemplo para qualquer texto padrão ou título na sidebar que não seja um link */
        /* Seletor de outros textos na sidebar (ATUALIZADO com a nova classe do pai) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 p, 
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h1,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h2,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h3,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h4,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h5,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h6 {
            color: #FFFFFF !important;
        }

        /* Estiliza o H1 do título "Contratos - 25/2024-SEMINF" */
        h1[data-testid="stMarkdownContainer"] {
            color: var(--text-color) !important;
        }
        
    </style>
""", unsafe_allow_html=True)

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
    
    st.markdown('<h1 data-testid="stMarkdownContainer">Contratos - 25/2024-SEMINF</h1>', unsafe_allow_html=True)

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