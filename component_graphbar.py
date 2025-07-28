import streamlit as st
import plotly.express as px

def mostrar_grafico(df, selecao_valor):
    df = df.copy()
    df["hierarquia"] = df["hierarquia"].astype(str).str.strip()
    df["nivel"] = df["hierarquia"].apply(lambda x: x.count(".") + 1)

    if selecao_valor == "Todos":
        # exibe apenas os tópicos de nível 1
        df_plot = df[df["hierarquia"].str.count(r"\.") == 0].copy()
    else:
        nivel_atual = str(selecao_valor).count(".") + 1
        prox_nivel  = nivel_atual + 1
        df_plot = df[
            (df["hierarquia"] == selecao_valor) |
            ((df["hierarquia"].str.startswith(selecao_valor + ".")) &
            (df["hierarquia"].str.count(r"\.") + 1 == prox_nivel))
        ].copy()

    # normalização
    if df_plot["previsto"].max() <= 1:
        df_plot["previsto"] *= 100
    if df_plot["concluido"].max() <= 1:
        df_plot["concluido"] *= 100

    st.markdown('<h3 style="margin-bottom: -50px;margin-top: -10px;">Comparativo de Projetos</h3>', unsafe_allow_html=True)
    if df_plot.empty:
        st.info("Nenhum subtópico encontrado para este item.")
        return
    
    altura_por_item = 10
    altura_total = max(230, len(df_plot) * altura_por_item)

    # --- Início da Modificação ---
    # Define a quantidade máxima de caracteres com base no número de tarefas
    if len(df_plot) > 7:
        max_chars = 12
    else:
        max_chars = 30

    # Aplica a abreviação condicional
    df_plot["tarefa_curta"] = df_plot["tarefa"].apply(
        lambda x: x if len(x) <= max_chars else x[:max_chars] + "..."
    )
    # --- Fim da Modificação ---

    fig = px.bar(
        df_plot, x="tarefa_curta", y=["previsto", "concluido"],
        labels={"value": "Percentual", "variable": "Tipo"},
        hover_data={"tarefa": True, "tarefa_curta": False},
        barmode="group", height=altura_total,
        color_discrete_map={"previsto": "#f08224", "concluido": "#3c3c3b"}
    )
    fig.update_layout(
        yaxis=dict(range=[0,100], tickformat=".0f", title="Percentual (%)"),
        xaxis_title="Tarefa", legend_title="", bargap=0.8,margin=dict(b=2)
    )
    fig.update_xaxes(tickangle=0, tickfont=dict(size=11))

    with st.container():
        st.markdown("""
            <div style="padding: 2px;">
        """, unsafe_allow_html=True)

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)