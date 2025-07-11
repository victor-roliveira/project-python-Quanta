import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from component_table import mostrar_tabela
from component_graphbar import mostrar_grafico
from component_graphbar_tasks_delay import mostrar_graficos_tarefas_atrasadas
import streamlit.components.v1 as components

# =========================
# Configurações de layout e estilo
# =========================
st.set_page_config(page_title="Dashboard Macaé", layout="wide")

st.markdown("""
    <style>
        html, body, .stApp {
            padding-top: 0px !important;
            margin-top: 0px !important;
        }

        .block-container {
            padding-top: 20px !important;
            padding-bottom: 20px !important;
        }
    </style>
""", unsafe_allow_html=True)

# =========================
# Carregar dados
# =========================
df = pd.read_excel("ProjectEmExcel_MKE.xlsx")

df = df[[
    "Número Hierárquico", "Nome da Tarefa", "Término",
    "%concluida prev. (Número10)", "% Concluída",
    "Responsável 01", "Responsável 02", "Nomes de Recursos", "Exe."
]].copy()

df.columns = [
    "hierarquia", "tarefa", "termino", "previsto", "concluido",
    "responsavel 1", "responsavel 2", "nome dos recursos", "execucao"
]

df["previsto"] = pd.to_numeric(df["previsto"], errors="coerce").fillna(0)
df["concluido"] = pd.to_numeric(df["concluido"], errors="coerce").fillna(0)
df["hierarchy_path"] = df["hierarquia"].astype(str).apply(lambda x: x.split("."))

df["barra_info"] = df.apply(lambda row: {
    "concluido": round(row["concluido"] * 100),
    "previsto": round(row["previsto"])
}, axis=1).apply(lambda x: str(x).replace("'", '"'))

colunas = list(df.columns)
idx = colunas.index("concluido")
colunas.remove("barra_info")
colunas.insert(idx + 1, "barra_info")
df = df[colunas]

# =========================
# Cabeçalho e navegação
# =========================
st.title("Acompanhamento Geral Macaé")

# =========================
# Abas de navegação
# =========================
aba_tabela, aba_atrasadas, aba_resumo = st.tabs(["📋 Tabela", "🚨 Atrasos Por Área", "ℹ️ Avanço Geral"])

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

with aba_resumo:
    st.markdown("""
        <style>
            .resumo-img {
                height: 1200px;
                width: 100%;
                object-fit: cover;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h3 style='text-align: center;'>Resumo Geral de Avanço</h3>", unsafe_allow_html=True)
    st.image("resumo_geral.png", use_container_width=True, output_format="PNG")
