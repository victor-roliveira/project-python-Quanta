import streamlit as st
import plotly.express as px

def mostrar_grafico(df):
    df["topico_nivel1"] = df["hierarquia"].astype(str).str.split(".").str[0].str.strip()
    df["topico_nivel2"] = df["hierarquia"].astype(str).apply(lambda x: ".".join(x.split(".")[:2]) if len(x.split(".")) > 1 else x).str.strip()

    opcoes_filtro = ["Todos os Tópicos"]
    topicos1_ord = sorted(df["topico_nivel1"].unique(), key=lambda x: int(x) if x.isdigit() else x)

    for t1 in topicos1_ord:
        nome_t1 = df[df["topico_nivel1"] == t1]["tarefa"].iloc[0]
        opcoes_filtro.append(f"{t1} - {nome_t1}")
        subtopicos = sorted(df[df["topico_nivel1"] == t1]["topico_nivel2"].unique(), key=lambda x: [int(i) if i.isdigit() else i for i in x.split(".")])
        for stp in subtopicos:
            if stp != t1:
                nome_stp = df[df["topico_nivel2"] == stp]["tarefa"].iloc[0]
                opcoes_filtro.append(f"  {stp} - {nome_stp}")

    selecao = st.sidebar.selectbox("Filtro de Tarefas", opcoes_filtro, index=0)

    if selecao == "Todos os Tópicos":
        selecao_valor = "Default"
    else:
        selecao_valor = selecao.strip().split(" ")[0]

    if selecao_valor == "Default":
        df_plot = df[df["topico_nivel1"].isin(["1", "2", "3", "4", "5", "6"])].copy()
    else:
        df_plot = df[df["hierarquia"].astype(str).str.startswith(selecao_valor + ".") | (df["hierarquia"].astype(str) == selecao_valor)].copy()

    if df_plot["previsto"].max() <= 1:
        df_plot["previsto"] *= 100
    if df_plot["concluido"].max() <= 1:
        df_plot["concluido"] *= 100

    st.markdown("---")
    st.subheader("📊 Comparativo de Tarefas")

    fig = px.bar(
        df_plot,
        x="tarefa",
        y=["previsto", "concluido"],
        labels={"value": "Percentual", "variable": "Tipo", "tarefa": "Tarefa"},
        barmode="group",
        height=500,
        color_discrete_map={
            "previsto": "#f08224",
            "concluido": "#ffffff"
        }
    )

    fig.update_layout(
        yaxis=dict(range=[0, 100], tickformat=".2f", title="Percentual (%)"),
        xaxis_title="Tarefa",
        legend_title=""
    )

    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
