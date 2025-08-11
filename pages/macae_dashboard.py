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
            
        /* Estilos da Sidebar */
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 {
            background-color: #333333;
            color: #FFFFFF;
        }
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a > span {
            color: #ffffff !important;
        }
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a:hover {
            background-color: #555555;
            border-radius: 5px;
        }
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a:hover > span {
            color: #00BFFF !important;
        }
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a[aria-current="page"] {
            background-color: #444444;
        }
        #root > div:nth-child(1) > div.withScreencast > div > div.stAppViewContainer.appview-container.st-emotion-cache-1yiq2ps.e4man110 > section > div.hideScrollbar.st-emotion-cache-jx6q2s.eu6y2f92 > div.st-emotion-cache-79elbk.ej6j6k40 > ul > div > li > div > a[aria-current="page"] > span {
            color: #FFD700 !important;
            font-weight: bold;
        }
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

    colunas_necessarias = {
        "Número da estrutura de tópicos": "hierarquia",
        "Nome da Tarefa": "tarefa",
        "Início": "inicio",
        "Término": "termino",
        "%concluida prev. (Número10)": "previsto",
        "% concluída": "concluido",
        "Responsável 01": "responsavel 1",
        "Responsável 02": "responsavel 2",
        "Nomes dos recursos": "nome dos recursos",
        "Exe.": "execucao",
        "Terceirizadas": "terceiros"
    }

    # Filtra o DataFrame para conter apenas as colunas necessárias e as renomeia.
    df_filtrado = df.rename(columns=lambda col: col.strip())[list(colunas_necessarias.keys())].copy()
    df_filtrado.rename(columns=colunas_necessarias, inplace=True)
    df = df_filtrado
    
    df["previsto"] = pd.to_numeric(df["previsto"], errors="coerce").fillna(0)
    df["concluido"] = pd.to_numeric(df["concluido"], errors="coerce").fillna(0)
    df["terceiros"] = pd.to_numeric(df["terceiros"], errors="coerce").fillna(0)
    
    df['inicio'] = df['inicio'].astype(str)
    df['termino'] = df['termino'].astype(str)

    df['inicio'] = df['inicio'].apply(lambda x: x.split(' ')[1] if ' ' in x else x)
    df['termino'] = df['termino'].apply(lambda x: x.split(' ')[1] if ' ' in x else x)

    df["inicio"] = pd.to_datetime(df["inicio"], format='%d/%m/%y', errors='coerce').dt.strftime('%d/%m/%Y')
    df["termino"] = pd.to_datetime(df["termino"], format='%d/%m/%y', errors='coerce').dt.strftime('%d/%m/%Y')
    
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

    colunas_para_remover = ["execucao", "terceiros"]
    df_tabela_geral = df.drop(columns=[col for col in colunas_para_remover if col in df.columns])
    linha_selecionada = mostrar_tabela(df_tabela_geral, limpar_selecao=limpar)

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
    st.markdown("<h6 style='text-align: left;'>LEGENDA: ✅ Concluído / ❌ Não Possui /❕Terceirizados / ❗ Não Iniciados Atrasados com Terceirizados / - Não Iniciados Internos</h3>", unsafe_allow_html=True)
    mostrar_tabela_projetos_especificos_aggrid(df, str(selecao_valor))
