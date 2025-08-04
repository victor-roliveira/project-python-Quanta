import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import json
from collections import OrderedDict

def mostrar_tabela_projetos_especificos_aggrid_marica(df_original):
    df = df_original.copy()

    df['tarefa'] = df['tarefa'].str.strip()
    path_to_name_map = df.set_index(df['hierarchy_path'].apply(tuple))['tarefa'].to_dict()
    projetos_principais_numeros = {'4', '5', '6'}

    # 1. Preparar DataFrame unificado para a tabela pivô (sem alterações aqui)
    df_nivel2 = df[df['hierarchy_path'].apply(lambda p: len(p) == 2 and p[0] in projetos_principais_numeros)]
    df_nivel3 = df[df['hierarchy_path'].apply(lambda p: len(p) == 3 and p[0] in projetos_principais_numeros)]
    pais_com_filhos = set(df_nivel3['hierarchy_path'].apply(lambda p: tuple(p[:2])))
    df_nivel2_folhas = df_nivel2[~df_nivel2['hierarchy_path'].apply(tuple).isin(pais_com_filhos)]
    df_para_pivo = pd.concat([df_nivel3, df_nivel2_folhas])

    if df_para_pivo.empty:
        return st.warning("Não foram encontradas tarefas de nível 2 ou 3 para os projetos 4, 5 e 6.")

    # 2. Preparar e criar a tabela pivô (sem alterações aqui)
    df_para_pivo['projeto_pai'] = df_para_pivo['hierarchy_path'].apply(lambda p: path_to_name_map.get(tuple(p[:1])))
    df_para_pivo['status_data'] = df_para_pivo.apply(
        lambda row: {'concluido': row['concluido'], 'previsto': row['previsto']},
        axis=1
    )
    df_para_pivo.dropna(subset=['projeto_pai'], inplace=True)
    tabela_pivo = df_para_pivo.pivot_table(
        index='projeto_pai',
        columns='tarefa',
        values='status_data',
        aggfunc='first'
    )

    # 3. Lógica de Progresso e formatação da tabela (sem alterações aqui)
    df_nivel1 = df[df['hierarchy_path'].apply(len) == 1]
    projeto_data_map = df_nivel1.set_index('tarefa')[['concluido', 'previsto']].to_dict('index')
    
    tabela_para_grid = tabela_pivo.reset_index()
    tabela_para_grid.rename(columns={'projeto_pai': 'Projeto'}, inplace=True)

    def get_progress_data(projeto_name):
        data = projeto_data_map.get(projeto_name)
        if data:
            progress_info = {
                'concluido': round(data.get('concluido', 0) * 100),
                'previsto': data.get('previsto', 0)
            }
            return json.dumps(progress_info)
        return None
        
    tabela_para_grid['Progresso'] = tabela_para_grid['Projeto'].apply(get_progress_data)
    
    cols = tabela_para_grid.columns.tolist()
    if 'Progresso' in cols:
        cols.insert(1, cols.pop(cols.index('Progresso')))
        tabela_para_grid = tabela_para_grid[cols]
    # 8. Definir os renderers JavaScript para a AgGrid.
    # Renderer para a barra de progresso (fornecido por você).
    barra_progress_renderer = JsCode("""
        function(params) {
            if (!params.value) return '';
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
                color = '#7f9bff';
            }

            const width = Math.min(Math.max(concluido, 0), 100);

            params.eGridCell.innerHTML = `
                <div style="width: 100%; background-color: #ddd; border-radius: 5px; height: 16px; margin-top: 5px;">
                    <div style="width: ${width}%; background-color: ${color}; height: 16px; border-radius: 5px;"></div>
                </div>
            `;
        }
    """)

    # Renderer para as células de tarefas individuais.
    cell_renderer_js = JsCode("""
        function(params) {
            const eGui = params.eGridCell;
            eGui.style.backgroundColor = 'transparent';
            eGui.style.color = 'black';
            eGui.style.fontWeight = 'normal';

            if (params.value == null || typeof params.value !== 'object') {
                return "❌";
            }

            const concluido_val = params.value.concluido || 0;
            const previsto_val = params.value.previsto || 0;
            const concluido_percent = Math.round(concluido_val * 100);

            if (concluido_percent === 100) {
                eGui.style.backgroundColor = '#28a745';
                eGui.style.color = 'white';
                eGui.style.fontWeight = 'bold';
                return '✔';
            } else if (concluido_percent < previsto_val) {
                eGui.style.backgroundColor = '#dc3545';
                eGui.style.color = 'white';
                return concluido_percent + '%';
            } else {
                eGui.style.color = 'white';
                return concluido_percent + '%🔄️';
            }
        }
    """)

    column_defs = [
        {"headerName": "Projeto", "field": "Projeto", "pinned": "left", "width": 350, "cellStyle": {"fontWeight": "bold", "textAlign": "left"}},
        {"headerName": "Progresso", "field": "Progresso", "pinned": "left", "width": 150, "cellRenderer": barra_progress_renderer}
    ]

    # Mapeia pais (Nível 2) para filhos (Nível 3)
    parent_child_map = {}
    for _, row in df_nivel3.iterrows():
        parent_path = tuple(row['hierarchy_path'][:2])
        parent_name = path_to_name_map.get(parent_path)
        if parent_name:
            if parent_name not in parent_child_map:
                parent_child_map[parent_name] = []
            # MUDANÇA 1: Garante que a lista de filhos para cada pai seja única
            child_name = row['tarefa']
            if child_name not in parent_child_map[parent_name]:
                parent_child_map[parent_name].append(child_name)

    # MUDANÇA 2: Criar uma lista ordenada e ÚNICA de nomes de tarefas de Nível 2
    df_nivel2_ordenado = df_nivel2.sort_values(by='hierarchy_path')
    ordered_unique_l2_names = df_nivel2_ordenado['tarefa'].drop_duplicates().tolist()
    
    # MUDANÇA 3: Iterar sobre a lista ÚNICA de nomes, não mais sobre o DataFrame com duplicatas
    for task_name_n2 in ordered_unique_l2_names:
        
        # CASO 1: A tarefa Nível 2 TEM filhos -> Criar um Grupo de Colunas
        if task_name_n2 in parent_child_map and parent_child_map[task_name_n2]:
            children_names = sorted(parent_child_map[task_name_n2])
            children_defs = [
                {"headerName": child_name, "field": child_name, "cellRenderer": cell_renderer_js}
                for child_name in children_names
            ]
            column_defs.append({"headerName": task_name_n2, "children": children_defs})
        
        # CASO 2: A tarefa Nível 2 NÃO TEM filhos (em nenhum dos projetos) -> Criar uma Coluna Simples
        elif task_name_n2 not in parent_child_map:
            column_defs.append({
                "headerName": task_name_n2,
                "field": task_name_n2,
                "cellRenderer": cell_renderer_js
            })

    # 5. Montar 'gridOptions' e chamar AgGrid (sem alterações aqui)
    gridOptions = {
        "columnDefs": column_defs,
        "defaultColDef": {"resizable": True, "sortable": True, "cellStyle": {"textAlign": "center"}, "minWidth": 150},
        "domLayout": 'normal',
    }

    AgGrid(
        tabela_para_grid,
        gridOptions=gridOptions,
        height=350,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        custom_css={
            ".ag-cell": {"font-size": "12px", "font-family": "'Raleway', sans-serif", "border-right": "2px solid white", "border-bottom": "2px solid white"},
            ".ag-header-cell-text, .ag-header-group-cell-label": {"font-size": "14px", "white-space": "normal"},
        },
    )