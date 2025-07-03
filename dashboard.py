import streamlit as st
import pandas as pd
from component_table import mostrar_tabela
from component_graphbar import mostrar_grafico

# =========================
# Carregar dados
# =========================
df = pd.read_excel("ProjectEmExcel_MKE.xlsx")

# Selecionar e renomear colunas
df = df[[
    "Número Hierárquico", "Nome da Tarefa",
    "%concluida prev. (Número10)", "% Concluída",
    "Responsável 01", "Responsável 02", "Nomes de Recursos"
]].copy()

df.columns = ["hierarquia", "tarefa", "previsto", "concluido", "responsavel 1", "responsavel 2", "nome dos recursos"]

df["previsto"] = pd.to_numeric(df["previsto"], errors="coerce").fillna(0)
df["concluido"] = pd.to_numeric(df["concluido"], errors="coerce").fillna(0)
df["hierarchy_path"] = df["hierarquia"].astype(str).apply(lambda x: x.split("."))
df["barra_concluido"] = df["concluido"].apply(lambda val: "█" * int(float(val) * 20) + " " * (20 - int(float(val) * 20)))

# Reordenar colunas
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
st.markdown("Explore o andamento das tarefas.")

# =========================
# Mostrar componentes
# =========================
mostrar_tabela(df)
mostrar_grafico(df)
