from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

def mostrar_tabela(df):
    # ✅ Criar coluna com emoji de status
    df["tarefa_status"] = df.apply(
        lambda row: ("🟢 " if row["concluido"] * 100 >= row["previsto"] else "🔴 ") + row["tarefa"],
        axis=1
    )

    # ✅ Corrigir tipo de hierarquia (str)
    df["hierarquia"] = df["hierarquia"].astype(str).str.strip()

    # ✅ Criar coluna topico (apenas para exibição no agrupamento)
    df["topico"] = df["hierarquia"]

    # ✅ Criar caminho de hierarquia para árvore
    df["hierarchy_path"] = df["hierarquia"].apply(lambda x: x.split("."))

    # ✅ Ordenar corretamente pelos níveis hierárquicos
    def hierarquia_sort_key(h):
        try:
            return [int(part) if part.isdigit() else part for part in h.split(".")]
        except:
            return [h]

    df = df.sort_values(by="hierarquia", key=lambda col: col.map(hierarquia_sort_key))

    # ✅ Reordenar colunas para colocar tarefa_status no lugar de 'tarefa'
    colunas = list(df.columns)
    colunas.remove("tarefa_status")
    colunas.insert(colunas.index("tarefa"), "tarefa_status")
    df = df[colunas]

    # ✅ Remover coluna 'topico' do DataFrame (será usada apenas no agrupamento)
    df = df.drop(columns=["topico"])

    # ✅ Configuração do AgGrid
    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_grid_options(
        treeData=True,
        animateRows=True,
        groupDefaultExpanded=0,
        getDataPath=JsCode("function(data) { return data.hierarchy_path; }"),
        autoGroupColumnDef={
            "headerName": "Tópico",
            "field": "hierarquia",
            "cellRendererParams": {
                "suppressCount": True,
                "innerRenderer": JsCode("function(params) { return params.value; }")
            },
            "pinned": "left",
            "minWidth": 100,
            "cellStyle": {"textAlign": "center"}
        }
    )

    # ✅ Ocultar colunas internas
    gb.configure_columns(["hierarquia", "hierarchy_path", "tarefa"], hide=True)

    # ✅ Coluna de tarefa com status visual
    gb.configure_column("tarefa_status", header_name="Tarefa", minWidth=250, maxWidth=400)

    gb.configure_column("previsto",
        header_name="% Previsto",
        type=["numericColumn"],
        maxWidth=120,
        cellStyle={"textAlign": "center"},
        valueFormatter=JsCode("function(params) { return (params.value).toFixed(0) + '%' }")
    )

    gb.configure_column("concluido",
        header_name="% Exe",
        type=["numericColumn"],
        maxWidth=120,
        cellStyle={"textAlign": "center"},
        valueFormatter=JsCode("function(params) { return (params.value * 100).toFixed(0) + '%' }")
    )

    gb.configure_column("barra_concluido",
        header_name="Barra de %",
        maxWidth=170, minWidth=170
    )

    gb.configure_column("responsavel 1", header_name="AT 1", maxWidth=120, cellStyle={"textAlign": "center"})
    gb.configure_column("responsavel 2", header_name="AT 2", maxWidth=120, cellStyle={"textAlign": "center"})
    gb.configure_column("nome dos recursos", header_name="Recurso", maxWidth=140, cellStyle={"textAlign": "center"})

    # ✅ Exibição final da tabela
    AgGrid(
        df,
        gridOptions=gb.build(),
        height=800,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        fit_columns_on_grid_load=True,
        custom_css={
            ".ag-cell": {
                "font-size": "10px",
                "font-weight": "800",
                "line-height": "22px",
            },
            ".ag-header-cell-text": {
                "font-size": "14px"
            },
            ".ag-header-cell-label": {
                "justify-content": "center",
                "align-items": "center"
            },
        }
    )
