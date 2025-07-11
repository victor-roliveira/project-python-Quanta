from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

def mostrar_tabela(df):
    df["tarefa_status"] = df.apply(
        lambda row: ("🟢 " if row["concluido"] * 100 >= row["previsto"] else "🔴 ") + row["tarefa"],
        axis=1
    )

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
        "minWidth": 60,
        "maxWidth": 150,
        "cellStyle": {"textAlign": "center"}
    },
    onRowGroupOpened=JsCode("""
        function(params) {
            const expandPaths = [];

            params.api.forEachNode(function(node) {
                if (node.expanded && node.data && node.data.hierarchy_path) {
                    expandPaths.push(node.data.hierarchy_path);
                }
            });

            window.expandPaths = expandPaths;
            params.api.redrawRows();
        }
    """),
    getRowStyle=JsCode("""
        function(params) {
            if (!window.expandPaths || window.expandPaths.length === 0) {
                return {}; // Nenhum nó expandido => estilo normal
            }

            const itemPath = params.data.hierarchy_path;

            // Verifica se a linha está em algum caminho expandido (ou é filho)
            for (let i = 0; i < window.expandPaths.length; i++) {
                const path = window.expandPaths[i];
                let match = true;

                for (let j = 0; j < path.length; j++) {
                    if (itemPath[j] !== path[j]) {
                        match = false;
                        break;
                    }
                }

                if (match) {
                    return { opacity: 1.0 };
                }
            }

            return { opacity: 0.3 };  // Fora de todos os ramos abertos
        }
    """)
)


    gb.configure_columns(["hierarquia", "hierarchy_path", "tarefa"], hide=True)
    gb.configure_column("tarefa_status", header_name="Tarefa", minWidth=250, maxWidth=400)
    gb.configure_column("termino", header_name="Término", cellStyle={"textAlign": "center"}, maxWidth=120)
    gb.configure_column("previsto",
        header_name="% Prev",
        cellStyle={"textAlign": "center"},
        type=["numericColumn"],
        maxWidth=90,
        valueFormatter=JsCode("function(params) { return (params.value).toFixed(0) + '%' }")
    )
    gb.configure_column("concluido",
        header_name="% Exe",
        cellStyle={"textAlign": "center"},
        type=["numericColumn"],
        maxWidth=90,
        valueFormatter=JsCode("function(params) { return (params.value * 100).toFixed(0) + '%' }")
    )

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

        if (concluido === 100) {
            params.eGridCell.innerHTML = `
                <div style="text-align: center; font-weight: bold; color: #2ebe00; margin-top: 2px;">
                    Finalizado ✅
                </div>
            `;
            return;
        }

        let color = '#7f9bff';
        if (concluido < previsto) {
            color = '#ff4d4d';
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

    gb.configure_column("responsavel 1", header_name="AT 1", cellStyle={"textAlign": "center"}, maxWidth=80)
    gb.configure_column("responsavel 2", header_name="AT 2", cellStyle={"textAlign": "center"}, maxWidth=80)
    gb.configure_column("nome dos recursos", header_name="Responsável", cellStyle={"textAlign": "center"}, maxWidth=150)

    grid_response = AgGrid(
        df,
        gridOptions=gb.build(),
        height=300,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        fit_columns_on_grid_load=True,
        update_mode='SELECTION_CHANGED',
        enable_row_selection=True,
        selection_mode='single',
        use_checkbox=False,  # <-- Clique direto na linha
        return_df=True,
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
        },
    )

    return grid_response['selected_rows']
