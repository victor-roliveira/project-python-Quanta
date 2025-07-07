import streamlit as st
import pandas as pd
from component_table import mostrar_tabela
from component_graphbar import mostrar_grafico
from component_graphbar_tasks_delay import mostrar_graficos_tarefas_atrasadas

# =========================
# Carregar dados
# =========================
df = pd.read_excel("ProjectEmExcel_MKE.xlsx")

df = df[[
    "Número Hierárquico", "Nome da Tarefa",
    "%concluida prev. (Número10)", "% Concluída",
    "Responsável 01", "Responsável 02", "Nomes de Recursos", "Exe."
]].copy()

df.columns = [
    "hierarquia", "tarefa", "previsto", "concluido",
    "responsavel 1", "responsavel 2", "nome dos recursos", "execucao"
]

df["previsto"] = pd.to_numeric(df["previsto"], errors="coerce").fillna(0)
df["concluido"] = pd.to_numeric(df["concluido"], errors="coerce").fillna(0)
df["hierarchy_path"] = df["hierarquia"].astype(str).apply(lambda x: x.split("."))
df["barra_concluido"] = df["concluido"].apply(lambda val: "█" * int(float(val) * 20) + " " * (20 - int(float(val) * 20)))

# Reordenar colunas (opcional)
colunas = list(df.columns)
idx = colunas.index("concluido")
colunas.remove("barra_concluido")
colunas.insert(idx + 1, "barra_concluido")
df = df[colunas]

# =========================
# Layout
# =========================
st.set_page_config(page_title="Dashboard com Hierarquia", layout="wide")

st.title("Acompanhamento Geral Macaé")

col1, col2, col3 =  st.columns([0.03, 0.03, 0.2])

with col1:
    if st.button("Voltar ao Início"):
        st.switch_page("dashboard.py") 

with col2:
    if st.button("Contrato Maricá"):
        st.switch_page("pages/marica_dashboard.py") 

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
