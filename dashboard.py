import streamlit as st
import pandas as pd
from component_table import mostrar_tabela
from component_graphbar import mostrar_grafico
from component_graphbar_tasks_delay import mostrar_graficos_tarefas_atrasadas

# =========================
# Carregar dados
# =========================
df = pd.read_excel("ProjectEmExcel_MKE.xlsx")

df = df[[  # selecione e renomeie conforme já fazia
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
st.title("📊 Acompanhamento Geral Macaé")
st.markdown("Explore o andamento das tarefas:")

# =========================
# Abas de navegação
# =========================
aba_tabela, aba_comparativo, aba_atrasadas = st.tabs(["📋 Tabela", "📊 Gráfico Comparativo", "🚨 Tarefas Atrasadas"])

with aba_tabela:
    mostrar_tabela(df)

with aba_comparativo:
    mostrar_grafico(df)

with aba_atrasadas:
    mostrar_graficos_tarefas_atrasadas(df)
