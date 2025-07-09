import streamlit as st
import plotly.express as px
import pandas as pd

def mostrar_graficos_tarefas_atrasadas(df):
    st.subheader("🚨 Atrasos por Área Técnica")
    
    df["execucao"] = pd.to_numeric(df["execucao"], errors="coerce").fillna(-1).astype(int)
    df["responsavel 1"] = df["responsavel 1"].fillna("").str.strip()
    df["responsavel 2"] = df["responsavel 2"].fillna("").str.strip()

    df_atrasadas = df[df["execucao"] == 2]

    areas = pd.concat([
        df_atrasadas[["responsavel 1"]].rename(columns={"responsavel 1": "Área"}),
        df_atrasadas[["responsavel 2"]].rename(columns={"responsavel 2": "Área"}),
    ])

    contagem_areas = areas[areas["Área"] != ""].value_counts().reset_index(name="Tarefas Atrasadas")

    fig = px.bar(
        contagem_areas,
        x="Área",
        y="Tarefas Atrasadas",
        color="Área",
        text="Tarefas Atrasadas",
        labels={"Área": "Área Técnica", "Tarefas Atrasadas": "Qtde. de Tarefas Atrasadas"},
        height=500, 
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, xaxis_title="Área Técnica", yaxis_title="Quantidade")
    st.plotly_chart(fig, use_container_width=True)