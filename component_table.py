from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

def mostrar_tabela(df):
   # Criar coluna com emoji de status
    df["tarefa_status"] = df.apply(
    lambda row: ("🟢 " if row["concluido"] * 100 >= row["previsto"] else "🔴 ") + row["tarefa"],
    axis=1
    )

    # Reordenar colunas para que tarefa_status fique no lugar de 'tarefa'
    colunas = list(df.columns)
    colunas.remove("tarefa_status")
    colunas.insert(colunas.index("tarefa"), "tarefa_status")
    df = df[colunas]

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_grid_options(
        treeData=True,
        animateRows=True,
        groupDefaultExpanded=0,
        getDataPath=JsCode("function(data) { return data.hierarchy_path; }")
    )

    # Esconder as colunas internas
    gb.configure_columns(["hierarquia", "hierarchy_path", "tarefa"], hide=True)

    # Exibir a nova coluna com status visual
    gb.configure_column("tarefa_status", header_name="Tarefa", minWidth=250, maxWidth=400)

    gb.configure_column("previsto",
        header_name="% Previsto",
        cellStyle={"textAlign": "center"},
        type=["numericColumn"],
        maxWidth=120,
        valueFormatter=JsCode("function(params) { return (params.value).toFixed(2) + '%' }")
    )
    gb.configure_column("concluido",
        header_name="% Exe",
        cellStyle={"textAlign": "center"},
        type=["numericColumn"],
        maxWidth=120,
        valueFormatter=JsCode("function(params) { return (params.value * 100).toFixed(2) + '%' }")
    )
    gb.configure_column("barra_concluido",
        header_name="Barra de %",
        headerStyle={"textAlign": "center"},
        cellStyle={"fontFamily": "monospace", "textAlign": "left"},
        maxWidth=130, minWidth=100
    )
    gb.configure_column("responsavel 1", header_name="AT 1", cellStyle={"textAlign": "center"}, maxWidth=120)
    gb.configure_column("responsavel 2", header_name="AT 2", cellStyle={"textAlign": "center"}, maxWidth=120)
    gb.configure_column("nome dos recursos", header_name="Recurso", headerStyle={"textAlign": "center"}, cellStyle={"textAlign": "center"}, maxWidth=140)

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
                "font-weight": "600",
                "line-height": "22px"
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
