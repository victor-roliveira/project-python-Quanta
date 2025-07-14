import streamlit as st
import pandas as pd
from component_table_marica import mostrar_tabela
from component_graphbar_marica import mostrar_grafico
from component_graphbar_tasks_delay import mostrar_graficos_tarefas_atrasadas
import streamlit.components.v1 as components

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
#df["barra_concluido"] = df["concluido"].apply(lambda val: "█" * int(float(val) * 20) + " " * (20 - int(float(val) * 20)))
df["barra_info"] = df.apply(lambda row: {
    "concluido": round(row["concluido"] * 100),
    "previsto": round(row["previsto"])
}, axis=1).apply(lambda x: str(x).replace("'", '"'))
# Reordenar colunas (opcional)
colunas = list(df.columns)
idx = colunas.index("concluido")
colunas.remove("barra_info") 
colunas.insert(idx + 1, "barra_info")
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
            padding-bottom: 20px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Acompanhamento Geral Maricá")

col1, col2, col3 =  st.columns([0.03, 0.03, 0.2])

#with col1:
 #   if st.button("Voltar ao Início"):
 #       st.switch_page("dashboard.py") 

#with col2:
   # if st.button("Contrato Macaé"):
    #    st.switch_page("pages/macae_dashboard.py") 

# =========================
# Abas de navegação
# =========================
aba_tabela, aba_atrasadas = st.tabs(["📋 Tabela", "🚨 Atrasos Por Área"])

with aba_tabela:
    df_tabela = df.drop(columns=["execucao"])
    linha_selecionada = mostrar_tabela(df_tabela)

    df["hierarquia"] = df["hierarquia"].astype(str).str.strip()
    df["nivel"] = df["hierarquia"].apply(lambda x: x.count(".") + 1)

    opcoes_filtro = ["Projetos Principais"]
    tarefas_ordenadas = sorted(df["hierarquia"].unique(), key=lambda x: [int(p) if p.isdigit() else p for p in x.split(".")])

    for h in tarefas_ordenadas:
        tarefa_nome = df[df["hierarquia"] == h]["tarefa"].iloc[0]
        indent = "  " * h.count(".")
        opcoes_filtro.append(f"{indent}{h} - {tarefa_nome}")

    if "mostrar_grafico" not in st.session_state:
        st.session_state.mostrar_grafico = False
    if "scroll_to_graph" not in st.session_state:
        st.session_state.scroll_to_graph = False

    # Atualiza a seleção baseada na linha clicada na tabela
    if linha_selecionada and "hierarquia" in linha_selecionada[0]:
        st.session_state.selecao_tabela = linha_selecionada[0]["hierarquia"]

    def expandir_e_scrollar():
        st.session_state.mostrar_grafico = True
        st.session_state.scroll_to_graph = True

    col1, col2, _ = st.columns([0.15, 0.15, 0.7])
    with col1:
        st.button(
            "📊 Visualizar Gráfico",
            key="btn_expandir",
            disabled=st.session_state.mostrar_grafico,
            on_click=expandir_e_scrollar
        )
    with col2:
        st.button(
            "🔽 Recolher Gráfico",
            key="btn_recolher",
            disabled=not st.session_state.mostrar_grafico,
            on_click=lambda: st.session_state.update({"mostrar_grafico": False})
        )

    st.markdown("")

    if st.session_state.mostrar_grafico:
            st.markdown('<div id="grafico-anchor"></div>', unsafe_allow_html=True)

            selecao = st.selectbox("Filtro de Projetos:", opcoes_filtro, index=0, key="grafico_filtro")
            selecao_valor = st.session_state.get("selecao_tabela")

            if not selecao_valor or selecao == "Projetos Principais":
                selecao_valor = selecao.strip().split(" ")[0] if selecao != "Projetos Principais" else "Todos"

            mostrar_grafico(df, selecao_valor)

            if st.session_state.scroll_to_graph:
                components.html(
                    """
                    <script>
                        const anchor = window.parent.document.getElementById("grafico-anchor");
                        if(anchor){
                            anchor.scrollIntoView({ behavior: "smooth", block: "start" });
                        }
                    </script>
                    """,
                    height=0
                )
                st.session_state.scroll_to_graph = False

with aba_atrasadas:
    mostrar_graficos_tarefas_atrasadas(df)
