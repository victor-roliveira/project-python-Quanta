import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import json

def mostrar_tabela_projetos_especificos_aggrid(df_original, filtro_nome=None):
    df = df_original.copy()

    # Garante que não haja espaços em branco extras nos nomes das tarefas.
    df['tarefa'] = df['tarefa'].str.strip()

    # 1. Criar um mapa de "caminho hierárquico" para "nome da tarefa".
    path_to_name_map = df.set_index(df['hierarchy_path'].apply(tuple))['tarefa'].to_dict()

    # 2. Definir os NÚMEROS dos projetos principais (nível 1) de interesse.
    projetos_principais_numeros = {'3', '4', '5'}

    # 3. Isolar as tarefas de nível 3 e 4.
    df_nivel3 = df[df['hierarchy_path'].apply(
        lambda p: isinstance(p, list) and len(p) == 3 and p[0] in projetos_principais_numeros
    )]
    df_nivel4 = df[df['hierarchy_path'].apply(
        lambda p: isinstance(p, list) and len(p) == 4 and p[0] in projetos_principais_numeros
    )]

    if df_nivel4.empty:
        return st.warning("Não foram encontradas tarefas detalhadas (nível 4) para os projetos 3, 4 e 5.")

    # 4. Preparar o DataFrame para a pivotagem.
    # O índice será o pai de nível 2, e as colunas serão as tarefas de nível 4.
    df_nivel4['etapa_avo'] = df_nivel4['hierarchy_path'].apply(lambda p: path_to_name_map.get(tuple(p[:2])))
    df_nivel4['tarefa_detalhada'] = df_nivel4['tarefa']
    
    df_nivel4['status_data'] = df_nivel4.apply(
        lambda row: {'concluido': row['concluido'], 'previsto': row['previsto']},
        axis=1
    )
    df_nivel4.dropna(subset=['etapa_avo'], inplace=True)

    # 5. Criar a tabela pivô.
    tabela_pivo = df_nivel4.pivot_table(
        index='etapa_avo', 
        columns='tarefa_detalhada', 
        values='status_data',
        aggfunc='first'
    )

    # 6. Obter os dados de progresso para a "Etapa" (nível 2).
    df_nivel2 = df[df['hierarchy_path'].apply(len) == 2]
    
    # Remove nomes de tarefas duplicados de nível 2 antes de criar o dicionário.
    df_nivel2_unique = df_nivel2.drop_duplicates(subset=['tarefa'], keep='first')
    etapa_data_map = df_nivel2_unique.set_index('tarefa')[['concluido', 'previsto']].to_dict('index')
    
    tabela_para_grid = tabela_pivo.reset_index()
    tabela_para_grid.rename(columns={'etapa_avo': 'Etapa'}, inplace=True)

    # Adiciona a coluna 'Progresso' com os dados para o renderer.
    def get_progress_data(etapa_name):
        data = etapa_data_map.get(etapa_name)
        if data:
            # O renderer espera 'concluido' como 0-100.
            progress_info = {
                'concluido': round(data.get('concluido', 0) * 100),
                'previsto': data.get('previsto', 0)
            }
            return json.dumps(progress_info)
        return None
        
    tabela_para_grid['Progresso'] = tabela_para_grid['Etapa'].apply(get_progress_data)
    
    # Reordena as colunas.
    cols = tabela_para_grid.columns.tolist()
    if 'Progresso' in cols:
        cols.insert(1, cols.pop(cols.index('Progresso')))
        tabela_para_grid = tabela_para_grid[cols]

    # 7. Definir os renderers JavaScript para a AgGrid.
    
    # Renderer para a barra de progresso.
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
        {"headerName": "Etapa", "field": "Etapa", "pinned": "left", "width": 350, "cellStyle": {"fontWeight": "bold", "textAlign": "left"}},
        {"headerName": "Progresso", "field": "Progresso", "pinned": "left", "width": 150, "cellRenderer": barra_progress_renderer}
    ]

    # Mapeia pais (Nível 3) para filhos (Nível 4)
    parent_child_map = {}
    for _, row in df_nivel4.iterrows():
        parent_path = tuple(row['hierarchy_path'][:3])
        parent_name = path_to_name_map.get(parent_path)
        if parent_name:
            if parent_name not in parent_child_map:
                parent_child_map[parent_name] = []
            child_name = row['tarefa']
            if child_name not in parent_child_map[parent_name]:
                parent_child_map[parent_name].append(child_name)
    
    # Cria uma lista ordenada e ÚNICA de nomes de tarefas de Nível 3.
    df_nivel3_ordenado = df_nivel3.sort_values(by='hierarchy_path')
    ordered_unique_l3_names = df_nivel3_ordenado['tarefa'].drop_duplicates().tolist()

    # Itera sobre a lista de nomes de nível 3 para criar as colunas.
    for task_name_n3 in ordered_unique_l3_names:
        # CASO 1: A tarefa Nível 3 TEM filhos (nível 4) -> Cria um Grupo de Colunas.
        if task_name_n3 in parent_child_map and parent_child_map[task_name_n3]:
            children_names = sorted(parent_child_map[task_name_n3])
            children_defs = [
                {"headerName": child_name, "field": child_name, "cellRenderer": cell_renderer_js}
                for child_name in children_names
            ]
            column_defs.append({"headerName": task_name_n3, "children": children_defs})
        
        # CASO 2: A tarefa Nível 3 NÃO TEM filhos -> Cria uma Coluna Simples.
        elif task_name_n3 not in parent_child_map:
            column_defs.append({
                "headerName": task_name_n3,
                "field": task_name_n3,
                "cellRenderer": cell_renderer_js
            })
    
    # 8. Montar 'gridOptions' e chamar AgGrid.
    gridOptions = {
        "columnDefs": column_defs,
        "defaultColDef": {"resizable": True, "sortable": True, "cellStyle": {"textAlign": "center"}, "minWidth": 150},
        "domLayout": 'normal',
    }

    AgGrid(
        tabela_para_grid,
        gridOptions=gridOptions,
        height=700,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        custom_css={
            ".ag-cell": {
                "font-size": "12px",
                "font-family": "'Raleway', sans-serif",
                "border-right": "2px solid white",
                "border-bottom": "2px solid white"
            },
            ".ag-header-cell-text, .ag-header-group-cell-label": {
                "font-size": "14px",
                "white-space": "normal",
            },
        },
    )
   