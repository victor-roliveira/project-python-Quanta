import streamlit as st
import plotly.express as px

def mostrar_grafico(df, selecao_valor):
    df["hierarquia"] = df["hierarquia"].astype(str).str.strip()
    df["nivel"] = df["hierarquia"].apply(lambda x: x.count(".") + 1)

    if selecao_valor == "Todos":
        # Mostrar apenas tópicos principais (nível 1 → sem pontos)
        df_plot = df[df["hierarquia"].str.count(r"\.") == 0].copy()
    else:
        nivel_atual = selecao_valor.count(".") + 1
        proximo_nivel = nivel_atual + 1

        df_plot = df[
            (df["hierarquia"].str.startswith(selecao_valor + ".")) &
            (df["hierarquia"].str.count(r"\.") + 1 == proximo_nivel)
        ].copy()

    # Normalização de porcentagens
    if df_plot["previsto"].max() <= 1:
        df_plot["previsto"] *= 100
    if df_plot["concluido"].max() <= 1:
        df_plot["concluido"] *= 100

    st.subheader("Comparativo de Projetos")

    if df_plot.empty:
        st.info("Nenhum subtópico encontrado para este item.")
        return

    fig = px.bar(
        df_plot,
        x="tarefa",
        y=["previsto", "concluido"],
        labels={"value": "Percentual", "variable": "Tipo", "tarefa": "Tarefa"},
        barmode="group",
        height=500,
        color_discrete_map={
            "previsto": "#f08224",
            "concluido": "#3c3c3b"
        }
    )

    fig.update_layout(
        yaxis=dict(range=[0, 100], tickformat=".0f", title="Percentual (%)"),
        xaxis_title="Tarefa",
        legend_title="",
        bargap=0.6
    )

    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
