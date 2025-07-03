from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

def mostrar_tabela(df):
    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_grid_options(
        treeData=True,
        animateRows=True,
        groupDefaultExpanded=0,
        getDataPath=JsCode("function(data) { return data.hierarchy_path; }")
    )

    gb.configure_columns(["hierarquia", "hierarchy_path"], hide=True)
    gb.configure_column("tarefa", header_name="Tarefa", minWidth=300, maxWidth=400)
    gb.configure_column("previsto",
        header_name="% Previsto",
        cellStyle={"textAlign": "center"},
        type=["numericColumn"],
        maxWidth=120,
        valueFormatter=JsCode("function(params) { return (params.value).toFixed(2) + '%' }")
    )
    gb.configure_column("concluido",
        header_name="% Concluído",
        cellStyle={"textAlign": "center"},
        type=["numericColumn"],
        maxWidth=120,
        valueFormatter=JsCode("function(params) { return (params.value * 100).toFixed(2) + '%' }")
    )
    gb.configure_column("barra_concluido",
        header_name="Barra de %",
        headerStyle={"textAlign": "center"},
        cellStyle={"fontFamily": "monospace", "textAlign": "left"},
        maxWidth=220, minWidth=200
    )
    gb.configure_column("responsavel 1", header_name="AT 1", cellStyle={"textAlign": "center"}, maxWidth=120)
    gb.configure_column("responsavel 2", header_name="AT 2", cellStyle={"textAlign": "center"}, maxWidth=120)
    gb.configure_column("nome dos recursos", header_name="Recurso", headerStyle={"textAlign": "center"}, cellStyle={"textAlign": "center"}, maxWidth=140)

    AgGrid(
        df,
        gridOptions=gb.build(),
        height=450,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        fit_columns_on_grid_load=True,
        custom_css={
            "#agridToolBar": {
                "font-size": "18px"
            },
            ".ag-cell": { 
                "font-size": "16px",
                "line-height": "22px"
            },
            ".ag-header-cell-text": {
                "font-size": "12px",
            },
            ".ag-header-cell-label": {
                "justify-content": "center",  
                "align-items": "center"        
            },
        }
    )
