import streamlit as st
import pandas as pd
from component_table_marica import mostrar_tabela
from component_graphbar_marica import mostrar_grafico
from component_graphbar_tasks_delay import mostrar_graficos_tarefas_atrasadas

# =========================
# Carregar dados
# =========================
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
df["barra_concluido"] = df["concluido"].apply(lambda val: "█" * int(float(val) * 20) + " " * (20 - int(float(val) * 20)))
df["barra_concluido"] = (df["concluido"] * 100).round(0)

# Reordenar colunas (opcional)
colunas = list(df.columns)
idx = colunas.index("concluido")
colunas.remove("barra_concluido")
colunas.insert(idx + 1, "barra_concluido")
df = df[colunas]

# =========================
# Layout
# =========================
st.set_page_config(page_title="Dashboard Maricá", layout="wide")

st.markdown("""
    <style>
        html, body, .stApp {
            padding-top: 0px !important;
            margin-top: 0px !important;
        }

        /* Opcional: reduz ainda mais o espaço do container principal */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 0px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Acompanhamento Geral Maricá")

col1, col2, col3 =  st.columns([0.03, 0.03, 0.2])

with col1:
    if st.button("Voltar ao Início"):
        st.switch_page("dashboard.py") 

with col2:
    if st.button("Contrato Macaé"):
        st.switch_page("pages/macae_dashboard.py") 

# =========================
# Abas de navegação
# =========================
aba_tabela, aba_comparativo, aba_atrasadas = st.tabs(["📋 Tabela", "📊 Gráfico Comparativo", "🚨 Tarefas Atrasadas"])

with aba_tabela:
    df_tabela = df.drop(columns=["execucao"])
    mostrar_tabela(df_tabela)


with aba_comparativo:
    # Preparar filtro hierárquico
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
