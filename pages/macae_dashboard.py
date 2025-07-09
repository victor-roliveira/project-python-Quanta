import streamlit as st
import pandas as pd
from component_table import mostrar_tabela
from component_graphbar import mostrar_grafico
from component_graphbar_tasks_delay import mostrar_graficos_tarefas_atrasadas

# =========================
# Configurações de layout e estilo
# =========================
st.set_page_config(page_title="Dashboard Macaé", layout="wide")

st.markdown("""
    <style>
        html, body, .stApp {
            padding-top: 0px !important;
            margin-top: 0px !important;
        }

        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 0px !important;
        }
    </style>
""", unsafe_allow_html=True)

# =========================
# Carregar dados
# =========================
df = pd.read_excel("ProjectEmExcel_MKE.xlsx")

df = df[[
    "Número Hierárquico", "Nome da Tarefa", "Término",
    "%concluida prev. (Número10)", "% Concluída",
    "Responsável 01", "Responsável 02", "Nomes de Recursos", "Exe."
]].copy()

df.columns = [
    "hierarquia", "tarefa", "termino", "previsto", "concluido",
    "responsavel 1", "responsavel 2", "nome dos recursos", "execucao"
]

df["previsto"] = pd.to_numeric(df["previsto"], errors="coerce").fillna(0)
df["concluido"] = pd.to_numeric(df["concluido"], errors="coerce").fillna(0)
df["hierarchy_path"] = df["hierarquia"].astype(str).apply(lambda x: x.split("."))

# Criar string JSON-like com os dados necessários para a barra
df["barra_info"] = df.apply(lambda row: {
    "concluido": round(row["concluido"] * 100),
    "previsto": round(row["previsto"])
}, axis=1).apply(lambda x: str(x).replace("'", '"'))

# ✅ Reordenar colunas
colunas = list(df.columns)
idx = colunas.index("concluido")
colunas.remove("barra_info")
colunas.insert(idx + 1, "barra_info")
df = df[colunas]

# =========================
# Cabeçalho e navegação
# =========================
st.title("Acompanhamento Geral Macaé")

col1, col2, col3 = st.columns([0.03, 0.03, 0.2])

with col1:
    if st.button("Voltar ao Início"):
        st.switch_page("dashboard.py")

with col2:
    if st.button("Contrato Maricá"):
        st.switch_page("pages/marica_dashboard.py")

# =========================
# Abas de navegação
# =========================
aba_tabela, aba_comparativo, aba_atrasadas, aba_resumo = st.tabs(["📋 Tabela", "📊 Gráfico Comparativo", "🚨 Atrasos Por Área", "ℹ️ Avanço Geral"])

with aba_tabela:
    df_tabela = df.drop(columns=["execucao"])
    mostrar_tabela(df_tabela)

with aba_comparativo:
    df["hierarquia"] = df["hierarquia"].astype(str).str.strip()
    df["nivel"] = df["hierarquia"].apply(lambda x: x.count(".") + 1)

    opcoes_filtro = ["Projetos Principais"]
    tarefas_ordenadas = sorted(df["hierarquia"].unique(), key=lambda x: [int(p) if p.isdigit() else p for p in x.split(".")])

    for h in tarefas_ordenadas:
        tarefa_nome = df[df["hierarquia"] == h]["tarefa"].iloc[0]
        indent = "  " * h.count(".")
        opcoes_filtro.append(f"{indent}{h} - {tarefa_nome}")

    selecao = st.selectbox("Filtro de Projetos:", opcoes_filtro, index=0)
    selecao_valor = selecao.strip().split(" ")[0] if selecao != "Projetos Principais" else "Todos"

    mostrar_grafico(df, selecao_valor)

with aba_atrasadas:
    mostrar_graficos_tarefas_atrasadas(df)

with aba_resumo:
    st.markdown("""
        <style>
            .resumo-img {
                height: 1200px;
                width: 100%;
                object-fit: cover;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center;'>Resumo Geral de Avanço</h3>", unsafe_allow_html=True)
    st.image("resumo_geral.png", use_container_width=True, output_format="PNG")
