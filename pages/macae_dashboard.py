import streamlit as st
import pandas as pd
import time
from component_table import mostrar_tabela
from component_graphbar import mostrar_grafico
from component_graphbar_tasks_delay import mostrar_graficos_tarefas_atrasadas
from auth_session import protect_page
from component_overall import mostrar_tabela_projetos_especificos_aggrid

st.set_page_config(page_title="Dashboard Macaé", page_icon="icone-quanta.png",layout="wide")
st.logo("logo-quanta-oficial.png", size="large")

protect_page()

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
        /* Seletor para o container principal da sidebar (ATUALIZADO) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 {
            background-color: #333333; /* Um cinza escuro para a sidebar */
            color: #FFFFFF; /* Cor do texto geral dentro da sidebar para contraste */
        }
        
        /* Estiliza o TEXTO dentro dos ITENS (páginas/links) da sidebar (ATUALIZADO) */
        /* Removido o ':nth-child(1)' para aplicar a todos os itens */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a > span {
            color: #ffffff !important; /* Exemplo: Azul claro para o texto dos links */
            /* Você pode adicionar outras propriedades aqui, como: */
            /* font-weight: bold; */
        }

        /* Estiliza o HOVER (quando o mouse passa por cima) dos itens da sidebar (ATUALIZADO) */
        /* Note que o :hover é aplicado ao <a> pai para que toda a área do link reaja */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a:hover {
            background-color: #555555; /* Um fundo levemente mais claro no hover */
            border-radius: 5px; /* Adiciona bordas arredondadas no hover */
        }
        /* Estiliza o texto do item no HOVER (ATUALIZADO) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a:hover > span {
            color: #00BFFF !important; /* Um azul mais forte no hover para o texto */
        }


        /* Estiliza o item ATIVO (página atualmente selecionada) na sidebar (ATUALIZADO) */
        /* O [aria-current="page"] é aplicado ao <a> pai */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a[aria-current="page"] {
            background-color: #444444; /* Fundo diferente para a página ativa */
        }
        /* Estiliza o texto do item ATIVO (ATUALIZADO) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a[aria-current="page"] > span {
            color: #FFD700 !important; /* Exemplo: Amarelo para a página ativa */
            font-weight: bold; /* Deixa o texto em negrito */
        }
            
        /* Exemplo para qualquer texto padrão ou título na sidebar que não seja um link (ATUALIZADO) */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 p, 
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h1,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h2,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h3,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h4,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h5,
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 h6 {
            color: #FFFFFF !important;
        }        
    </style>
""", unsafe_allow_html=True)
@st.cache_data 
def carregar_dados():
    df = pd.read_excel("ProjectEmExcel_MKE.xlsx")

    df.dropna(subset=['Nome da Tarefa'], inplace=True)

    df = df[[ 
        "Número da estrutura de tópicos", "Nome da Tarefa", "Término",
        "%concluida prev. (Número10)", "% concluída",
        "Responsável 01", "Responsável 02", "Nomes dos recursos", "Exe.",
        "Terceirizadas"
    ]].copy()

    df.columns = [
        "hierarquia", "tarefa", "termino", "previsto", "concluido",
        "responsavel 1", "responsavel 2", "nome dos recursos", "execucao",
        "terceiros"
    ]

    df["previsto"] = pd.to_numeric(df["previsto"], errors="coerce").fillna(0)
    df["concluido"] = pd.to_numeric(df["concluido"], errors="coerce").fillna(0)
    df["terceiros"] = pd.to_numeric(df["terceiros"], errors="coerce").fillna(0)
    df["hierarchy_path"] = df["hierarquia"].astype(str).apply(lambda x: x.split("."))

    df["barra_info"] = df.apply(lambda row: {
        "concluido": round(row["concluido"] * 100),
        "previsto": round(row["previsto"])
    }, axis=1).apply(lambda x: str(x).replace("'", '"'))

    colunas = list(df.columns)
    idx = colunas.index("concluido")
    colunas.remove("barra_info")
    colunas.insert(idx + 1, "barra_info")
    df = df[colunas]
    return df

df = carregar_dados()

st.markdown('<h1 style="margin-bottom: -30px;margin-top: 20px;">Acompanhamento Geral Macaé</h1>', unsafe_allow_html=True)

aba_tabela, aba_atrasadas, aba_resumo = st.tabs(["📋 Tabela", "🚨 Atrasos Por Área", "ℹ️ Avanço Geral"])

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
    
    with st.spinner("Carregando gráfico, por favor aguarde..."):
        time.sleep(1)
        mostrar_grafico(df, str(selecao_valor))

with aba_atrasadas:
    mostrar_graficos_tarefas_atrasadas(df)

with aba_resumo:
    st.markdown("<h6 style='text-align: left;'>LEGENDA: ✅ Concluído / 🔃 Igualado / 🔄️ Não Iniciado / ❌ Não Possui /👷🏼 Terceirizados</h3>", unsafe_allow_html=True)
    mostrar_tabela_projetos_especificos_aggrid(df, str(selecao_valor))