# ✅ component_table.py (adaptado para Maricá)
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

def mostrar_tabela(df):
    # Sinalizador visual de status
    df["tarefa_status"] = df.apply(
        lambda row: ("🟢 " if row["concluido"] * 100 >= row["previsto"] else "🔴 ") + row["tarefa"],
        axis=1
    )

    # Reordenar a coluna para substituir visualmente 'tarefa'
    colunas = list(df.columns)
    colunas.remove("tarefa_status")
    colunas.insert(colunas.index("tarefa"), "tarefa_status")
    df = df[colunas]

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
        "minWidth": 50,
        "maxWidth": 160,
        "cellStyle": {"textAlign": "center"}
    }
    )

    gb.configure_columns(["hierarquia", "hierarchy_path", "tarefa"], hide=True)
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
        maxWidth=150, minWidth=150
    )
    gb.configure_column("responsavel 1", header_name="Responsável", cellStyle={"textAlign": "center"}, maxWidth=120)
    gb.configure_column("responsavel 2", header_name="Recurso", cellStyle={"textAlign": "center"}, maxWidth=120)

    AgGrid(
        df,
        gridOptions=gb.build(),
        domLayout="autoHeight",
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        fit_columns_on_grid_load=True,
        custom_css={
            ".ag-cell": {
                "font-size": "12px",
                "font-weight": "600",
                "line-height": "22px",
                "font-family": "'Raleway', sans-serif"
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
