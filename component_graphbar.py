import streamlit as st
import plotly.express as px

def mostrar_grafico(df):
    df["hierarquia"] = df["hierarquia"].astype(str).str.strip()
    df["nivel"] = df["hierarquia"].apply(lambda x: x.count(".") + 1)

    # Construção da lista hierárquica com recuo
    opcoes_filtro = ["Todos os Tópicos"]
    tarefas_ordenadas = sorted(df["hierarquia"].unique(), key=lambda x: [int(p) if p.isdigit() else p for p in x.split(".")])

    for h in tarefas_ordenadas:
        tarefa_nome = df[df["hierarquia"] == h]["tarefa"].iloc[0]
        indent = "  " * (h.count("."))  # recuo visual baseado no nível
        opcoes_filtro.append(f"{indent}{h} - {tarefa_nome}")

    selecao = st.sidebar.selectbox("Filtro de Tarefas", opcoes_filtro, index=0)

    if selecao == "Todos os Tópicos":
        df_plot = df[df["hierarquia"].str.count(r"\.") == 0].copy()  # Apenas tópicos de primeiro nível
    else:
        selecao_valor = selecao.strip().split(" ")[0]  # pega apenas o código da hierarquia
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

    st.markdown("---")
    st.subheader("📊 Comparativo de Tarefas")

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
