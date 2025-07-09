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
    gb.configure_column("conclusao", header_name="Término",  cellStyle={"textAlign": "center"}, minWidth=100, maxWidth=150)

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
    # ✅ Renderer que usa innerHTML corretamente
    barra_progress_renderer = JsCode("""
    function(params) {
        let data;
        try {
            data = JSON.parse(params.value);
        } catch {
            data = { concluido: 0, previsto: 0 };
        }

        const concluido = data.concluido || 0;
        const previsto = data.previsto || 0;

        // Se estiver 100%, exibir texto finalizado
        if (concluido === 100) {
            params.eGridCell.innerHTML = `
                <div style="text-align: center; font-weight: bold; color: #2ebe00; margin-top: 2px;">
                    Finalizado ✅
                </div>
            `;
            return;
        }

        // Determinar a cor
        let color = '#7f9bff';  // azul padrão
        if (concluido < previsto) {
            color = '#ff4d4d';  // vermelho
        }

        const width = Math.min(Math.max(concluido, 0), 100);

        params.eGridCell.innerHTML = `
            <div style="width: 100%; background-color: #ddd; border-radius: 5px; height: 16px; margin-top: 5px;">
                <div style="width: ${width}%; background-color: ${color}; height: 16px; border-radius: 5px;"></div>
            </div>
        `;
    }
    """)

    gb.configure_column(
        "barra_info",
        header_name="Barra de %",
        cellRenderer=barra_progress_renderer,
        maxWidth=160,
        minWidth=160,
    )
    gb.configure_column("responsavel 1", header_name="Responsável", cellStyle={"textAlign": "center"}, maxWidth=150)
    gb.configure_column("responsavel 2", header_name="Recurso", cellStyle={"textAlign": "center"}, maxWidth=120)

    gb.configure_columns(["barra_concluido"], hide=True)
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
