import streamlit as st
import pandas as pd
from component_table_marica import mostrar_tabela
from component_graphbar_marica import mostrar_grafico
from component_graphbar_tasks_marica import mostrar_graficos_tarefas_atrasadas
from auth_session import protect_page

protect_page()

# Carregar dados
df = pd.read_excel("013A.xlsx")

df = df[[
    "D - N° Guia", "E - Nome Da Tarefa", "H - Conclusão",
    "% Ideal", "C - % Concluída",
    "K - Responsável", "L - Recurso", "B - Status"
]].copy()

df.columns = [
    "hierarquia", "tarefa", "conclusao", "previsto", "concluido",
    "responsavel 1", "responsavel 2", "execucao"
]

df["previsto"] = pd.to_numeric(df["previsto"], errors="coerce").fillna(0)
df["concluido"] = pd.to_numeric(df["concluido"], errors="coerce").fillna(0)
df["hierarchy_path"] = df["hierarquia"].astype(str).apply(lambda x: x.split("."))
df["barra_info"] = df.apply(lambda row: {
    "concluido": round(row["concluido"] * 100),
    "previsto": round(row["previsto"])
}, axis=1).apply(lambda x: str(x).replace("'", '"'))
# Reordenar colunas (opcional)
colunas = list(df.columns)
idx = colunas.index("concluido")
colunas.remove("barra_info") 
colunas.insert(idx + 1, "barra_info")
df = df[colunas]

# =========================
# Layout
# =========================
st.set_page_config(page_title="Dashboard Maricá", page_icon="icone-quanta.png",layout="wide")
st.logo("logo-quanta-oficial.png", size="large")

st.markdown("""
    <style>
        /* Ajusta o padding e margem gerais da aplicação */
        html, body, .stApp {
            padding-top: 0px !important;
            margin-top: 0px !important;
        }
        .block-container {
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }

        /* Torna a sidebar mais escura no tema claro */
        /* Seletor para o container principal da sidebar */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.elbt1zu0 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.e1quxfqw2 {
            background-color: #333333; /* Um cinza escuro para a sidebar */
            color: #FFFFFF; /* Cor do texto geral dentro da sidebar para contraste */
        }
        
        /* Estiliza o TEXTO dentro dos ITENS (páginas/links) da sidebar */
        /* Usando o seletor exato que você encontrou para o <span>, removendo ':nth-child(2)' para aplicar a TODOS */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.elbt1zu0 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.e1quxfqw2 > div.st-emotion-cache-79elbk.e16b601d0 > ul > li > div > a > span {
            color: #FFFFFF !important; /* Exemplo: Azul claro para o texto dos links */
            /* Você pode adicionar outras propriedades aqui, como: */
            /* font-weight: bold; */
        }

        /* Estiliza o HOVER (quando o mouse passa por cima) dos itens da sidebar */
        /* Lembre-se que o :hover deve ser aplicado ao <a> pai para que toda a área do link mude */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.elbt1zu0 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.e1quxfqw2 > div.st-emotion-cache-79elbk.e16b601d0 > ul > li > div > a:hover {
            background-color: #555555; /* Um fundo levemente mais claro no hover */
            border-radius: 5px; /* Adiciona bordas arredondadas no hover */
        }
        /* Estiliza o texto do item no HOVER */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.elbt1zu0 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.e1quxfqw2 > div.st-emotion-cache-79elbk.e16b601d0 > ul > li > div > a:hover > span {
            color: orange !important; /* Um azul mais forte no hover para o texto */
        }


        /* Estiliza o item ATIVO (página atualmente selecionada) na sidebar */
        /* O :hover deve ser aplicado ao <a> pai */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.elbt1zu0 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.e1quxfqw2 > div.st-emotion-cache-79elbk.e16b601d0 > ul > li > div > a[aria-current="page"] {
            background-color: #444444; /* Fundo diferente para a página ativa */
        }
        /* Estiliza o texto do item ATIVO */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.elbt1zu0 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.e1quxfqw2 > div.st-emotion-cache-79elbk.e16b601d0 > ul > li > div > a[aria-current="page"] > span {
            color: #FFD700 !important; /* Exemplo: Amarelo para a página ativa */
            font-weight: bold; /* Deixa o texto em negrito */
        }

        /* Exemplo para qualquer texto padrão ou título na sidebar que não seja um link */
        /* Mantenha esses seletores mais genéricos para texto que não esteja dentro dos links de página */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.elbt1zu0 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.e1quxfqw2 p, 
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.elbt1zu0 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.e1quxfqw2 h1,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.elbt1zu0 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.e1quxfqw2 h2,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.elbt1zu0 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.e1quxfqw2 h3,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.elbt1zu0 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.e1quxfqw2 h4,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.elbt1zu0 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.e1quxfqw2 h5,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.elbt1zu0 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.e1quxfqw2 h6 {
            color: #FFFFFF !important;
        }
        
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="margin-bottom: -40px;margin-top: 20px;">Acompanhamento Geral Maricá</h1>', unsafe_allow_html=True)

col1, col2, col3 =  st.columns([0.03, 0.03, 0.2])

# Abas de navegação
aba_tabela, aba_atrasadas = st.tabs(["📋 Tabela", "🚨 Atrasos Por Área"])

with aba_tabela:
    if "selecao_tabela" not in st.session_state:
        st.session_state.selecao_tabela = None
    if "limpar_selecao_tabela" not in st.session_state:
        st.session_state.limpar_selecao_tabela = False

    limpar = st.session_state.limpar_selecao_tabela
    linha_selecionada = mostrar_tabela(df.drop(columns=["execucao"]), limpar_selecao=limpar)

    if limpar:
        st.session_state.limpar_selecao_tabela = False

    if linha_selecionada == 0:
        st.session_state.selecao_tabela = None
    elif linha_selecionada:
        st.session_state.selecao_tabela = linha_selecionada

    selecao_valor = st.session_state.get("selecao_tabela")
    selecao_valor = selecao_valor if selecao_valor else "Todos"
    mostrar_grafico(df, str(selecao_valor))

with aba_atrasadas:
    mostrar_graficos_tarefas_atrasadas(df) 