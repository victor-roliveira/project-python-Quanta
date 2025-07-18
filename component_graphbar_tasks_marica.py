import streamlit as st
import plotly.express as px
import pandas as pd

def mostrar_graficos_tarefas_atrasadas(df):
    df_atrasadas = df[df["execucao"] == 2]  

    # Unir responsáveis em uma única lista
    responsaveis = df_atrasadas[["responsavel 1", "responsavel 2"]].fillna("")

    todas_areas = pd.concat([
        responsaveis["responsavel 1"],
        responsaveis["responsavel 2"]
    ], axis=0).reset_index(drop=True)

    contagem = todas_areas[todas_areas != ""].value_counts().reset_index()
    contagem.columns = ["Área Técnica", "Tarefas Atrasadas"]

    st.subheader("🚨 Atrasos por Área Técnica")

    fig = px.bar(
        contagem,
        x="Área Técnica",
        y="Tarefas Atrasadas",
        text="Tarefas Atrasadas",
        color="Área Técnica",
        height=400
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        showlegend=False,
        yaxis_title="Quantidade de Tarefas",
        xaxis_title="Área Técnica",
        yaxis=dict(range=[0, contagem["Tarefas Atrasadas"].max() + 20]),
    )

    fig.update_xaxes(tickangle=0, tickfont=dict(size=10))

    st.plotly_chart(fig, use_container_width=True)