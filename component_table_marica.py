from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

def mostrar_tabela(df_original):
    df = df_original.copy()

    df["tarefa_status"] = df.apply(
        lambda row: ("🟢 " if row["concluido"] * 100 >= row["previsto"] else "🔴 ") + row["tarefa"],
        axis=1
    )

    # Reorganiza colunas para exibição
    colunas = list(df.columns)
    colunas.remove("tarefa_status")
    colunas.insert(colunas.index("tarefa"), "tarefa_status")
    df = df[colunas]

    gb = GridOptionsBuilder.from_dataframe(df)

    gb.configure_grid_options(
        treeData=True,
        animateRows=True,
        groupDefaultExpanded=0,
        rowSelection='single',
        suppressRowClickSelection=False,
        rowStyle={"cursor": "pointer"},
        getDataPath=JsCode("function(data) { return data.hierarchy_path; }"),
        getRowClass=JsCode("""
            function(params) {
                if (params.node.isSelected()) {
                    return 'selected-row';
                }
                return '';
            }
        """),
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

    # Ocultar apenas visualmente
    gb.configure_columns(["hierarquia", "hierarchy_path", "tarefa"], hide=True)
    gb.configure_column("tarefa_status", header_name="Tarefa", minWidth=350, maxWidth=520)
    gb.configure_column("conclusao", header_name="Término", cellStyle={"textAlign": "center"}, maxWidth=100)
    #gb.configure_column("termino", header_name="Término", cellStyle={"textAlign": "center"}, maxWidth=120)

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

    gb.configure_column("barra_info", header_name="Barra de %", cellRenderer=barra_progress_renderer, maxWidth=160)
    gb.configure_column("responsavel 1", header_name="Responsável", cellStyle={"textAlign": "center"}, maxWidth=140)
    gb.configure_column("responsavel 2", header_name="AT", cellStyle={"textAlign": "center"}, maxWidth=80)
    #gb.configure_column("nome dos recursos", header_name="Responsável", cellStyle={"textAlign": "center"}, maxWidth=150)

    # Renderização da AgGrid
    response = AgGrid(
        df,
        gridOptions=gb.build(),
        height=300,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        fit_columns_on_grid_load=True,
        update_mode='SELECTION_CHANGED',
        enable_row_selection=True,
        selection_mode='single',
        use_checkbox=False,
        return_df=True,
        custom_css={
            ".ag-cell": {
                "font-size": "12px",
                "font-weight": "100",
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
            ".selected-row": {
                "background-color": "#394867 !important",
                "color": "white !important"
            }
        },
    )

    # 🔁 Pegamos a linha diretamente do df_original, comparando com o índice
    selected = response.selected_rows

    if selected is not None and not selected.empty:
        hierarquia = selected.iloc[0].get("hierarquia")
        return hierarquia
    return None