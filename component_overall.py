import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, JsCode
import json

def mostrar_tabela_projetos_especificos_aggrid(df_original, filtro_nome=None):
    df = df_original.copy()
    df['tarefa'] = df['tarefa'].str.strip()

    # --- ETAPA 1: PREPARAÇÃO DOS DADOS E IDENTIFICADORES ---

    df['hierarchy_path'] = df['hierarchy_path'].apply(lambda p: [str(i) for i in p] if isinstance(p, list) else [])
    df['hierarchy_id'] = df['hierarchy_path'].apply(lambda p: '.'.join(p))
    
    projetos_principais_numeros = {'3', '4', '5'}
    df_escopo = df[df['hierarchy_path'].apply(lambda p: len(p) > 0 and p[0] in projetos_principais_numeros)].copy()

    id_to_name_map = df.set_index('hierarchy_id')['tarefa'].to_dict()

    def get_name_path(path_list):
        return tuple(id_to_name_map.get('.'.join(path_list[:i+1]), '') for i in range(len(path_list)))

    df_escopo['name_path'] = df_escopo['hierarchy_path'].apply(get_name_path)

    # --- INÍCIO DA CORREÇÃO ---
    # Adiciona 'inicio' ao dicionário de status.
    status_by_name_path = df_escopo.set_index('name_path')[['concluido', 'previsto', 'terceiros', 'inicio']].to_dict('index')
    # --- FIM DA CORREÇÃO ---

    def natural_sort_key(hid):
        return tuple(int(x) for x in hid.split('.'))

    # --- ETAPA 2: DEFINIR O MODELO DAS COLUNAS E CONSTRUIR A HIERARQUIA ---

    etapas_df = df[df['hierarchy_path'].apply(lambda p: len(p) == 2 and p[0] in projetos_principais_numeros)].copy()
    etapas_df['sort_key'] = etapas_df['hierarchy_id'].apply(natural_sort_key)
    etapas_df.sort_values(by='sort_key', inplace=True)
    etapas_para_mostrar = etapas_df[['hierarchy_id', 'tarefa']].to_records(index=False)

    if etapas_para_mostrar.size == 0:
        return st.warning("Nenhuma etapa (nível 2) encontrada para os projetos.")

    template_etapa_id = etapas_para_mostrar[0][0]

    template_parent_child_map = {}
    template_descendants = df_escopo[df_escopo['hierarchy_path'].apply(
        lambda p: len(p) > 2 and '.'.join(p[:2]) == template_etapa_id
    )]

    leaf_name_paths_relative = []
    for _, row in template_descendants.iterrows():
        parent_id = '.'.join(row['hierarchy_path'][:-1])
        if parent_id not in template_parent_child_map:
            template_parent_child_map[parent_id] = []
        template_parent_child_map[parent_id].append(row['hierarchy_id'])
        
        is_leaf = row['hierarchy_id'] not in df_escopo['hierarchy_path'].apply(lambda p: '.'.join(p[:-1]) if len(p) > 1 else None).unique()
        if is_leaf:
            leaf_name_paths_relative.append(row['name_path'][2:])


    barra_progress_renderer = JsCode("""
        function(params) {
            if (!params.value) return '';
            let data;
            try { data = JSON.parse(params.value); } catch { data = { concluido: 0, previsto: 0 }; }
            const concluido = data.concluido || 0;
            if (concluido === 100) {
                params.eGridCell.innerHTML = `<div style="text-align: center; font-weight: bold; color: #2ebe00; margin-top: 2px;">Finalizado ✅</div>`;
                return;
            }
            let color = '#7f9bff';
            const width = Math.min(Math.max(concluido, 0), 100);
            params.eGridCell.innerHTML = `<div style="width: 100%; background-color: #ddd; border-radius: 5px; height: 16px; margin-top: 5px;"><div style="width: ${width}%; background-color: ${color}; height: 16px; border-radius: 5px;"></div></div>`;
        }
    """)

    cell_renderer_js = JsCode("""
        function(params) {
            const eGui = params.eGridCell;
            eGui.style.backgroundColor = 'transparent'; eGui.style.color = 'black'; eGui.style.fontWeight = 'normal';
            if (params.value == null || typeof params.value !== 'object') { return "❌"; }

            const concluido_val = params.value.concluido || 0;
            const previsto_val = params.value.previsto || 0;
            const terceiros_val = params.value.terceiros || 0;
            const inicio_str = params.value.inicio;
            const concluido_percent = Math.round(concluido_val * 100);

            // Lógica para tarefas NÃO INICIADAS (0%)
            if (concluido_percent === 0) {
                if (terceiros_val > 0) { // Se tiver terceiros
                    if (inicio_str) {
                        const today = new Date();
                        today.setHours(0, 0, 0, 0);
                        
                        const parts = inicio_str.split('/');
                        const startDate = new Date(parts[2], parts[1] - 1, parts[0]);
                        startDate.setHours(0, 0, 0, 0);
                        
                        if (today > startDate) { // Atrasada
                            eGui.style.color = 'red';
                        } else { // Não atrasada
                            eGui.style.color = 'white';
                        }
                    } else {
                        eGui.style.color = 'white'; // Padrão se não houver data de início
                    }
                    eGui.style.fontWeight = 'bold';
                    return ' !';
                } else { // Se não tiver terceiros
                    return '➖';
                }
            }
            
            // Lógica para tarefas JÁ INICIADAS (> 0%)
            const terceiros_indicator = terceiros_val > 0 ? '❕' : '';
            let text_to_display = '';

            if (concluido_percent === 100) {
                eGui.style.color = '#00ff07'; eGui.style.fontWeight = 'bold';
                text_to_display = '✔';
            } else if (concluido_percent < previsto_val) {
                eGui.style.backgroundColor = '#dc3545'; eGui.style.color = 'white';
                text_to_display = concluido_percent + '%';
            } else if (concluido_percent > previsto_val) {
                eGui.style.backgroundColor = "#0cc500"; eGui.style.color = 'white'; eGui.style.fontWeight = 'bold';
                text_to_display = concluido_percent + '%';
            } else { // Igual ao previsto
                eGui.style.color = 'black'; eGui.style.fontWeight = 'bold';
                text_to_display = concluido_percent + '%';
            }
            
            return text_to_display + terceiros_indicator;
        }
    """)

    def build_nested_cols(parent_id, parent_name_path):
        children_defs = []
        child_ids = sorted(template_parent_child_map.get(parent_id, []), key=natural_sort_key)
        
        for child_id in child_ids:
            child_name = id_to_name_map.get(child_id, "N/A")
            current_name_path = parent_name_path + (child_name,)
            
            field_id = "|".join(current_name_path[2:])

            if child_id in template_parent_child_map:
                children = build_nested_cols(child_id, current_name_path)
                if children:
                    children_defs.append({"headerName": child_name, "children": children})
            else:
                children_defs.append({"headerName": child_name, "field": field_id, "width": 70, "cellRenderer": cell_renderer_js, "headerClass": "vertical-header"})
        return children_defs

    template_etapa_name = id_to_name_map.get(template_etapa_id, "")
    template_name_path_base = tuple(id_to_name_map.get('.'.join(template_etapa_id.split('.')[:i+1])) for i in range(2))

    column_defs = [
        {"headerName": "Etapa", "field": "Etapa", "pinned": "left", "width": 160, "cellStyle": {"fontWeight": "bold", "textAlign": "left"}},
        {"headerName": "Progresso", "field": "Progresso", "pinned": "left", "width": 120, "cellRenderer": barra_progress_renderer}
    ]
    column_defs.extend(build_nested_cols(template_etapa_id, template_name_path_base))

    # --- ETAPA 3: CONSTRUIR O DATAFRAME FINAL PARA O AGGRID ---

    etapa_progress_map = df[df['hierarchy_path'].apply(len) == 2].set_index('hierarchy_id')[['concluido', 'previsto']].to_dict('index')

    grid_data = []
    for etapa_id, etapa_name in etapas_para_mostrar:
        row_data = {'Etapa': etapa_name, 'Progresso': None}
        
        progress_info = etapa_progress_map.get(etapa_id)
        if progress_info:
            row_data['Progresso'] = json.dumps({'concluido': round(progress_info.get('concluido', 0) * 100), 'previsto': progress_info.get('previsto', 0)})

        etapa_base_name_path = tuple(id_to_name_map.get('.'.join(etapa_id.split('.')[:i+1])) for i in range(2))

        for rel_name_path in leaf_name_paths_relative:
            lookup_key = etapa_base_name_path + rel_name_path
            field_key = "|".join(rel_name_path)
            
            status = status_by_name_path.get(lookup_key)
            row_data[field_key] = status
            
        grid_data.append(row_data)

    tabela_para_grid = pd.DataFrame(grid_data)

    # --- ETAPA 4: RENDERIZAR A TABELA ---
    gridOptions = {
        "columnDefs": column_defs,
        "defaultColDef": {"resizable": True, "sortable": False, "cellStyle": {"textAlign": "center"}},
        "domLayout": 'normal', "groupHeaderHeight": 45, "headerHeight": 35,
    }

    AgGrid(
        tabela_para_grid, gridOptions=gridOptions, height=700, allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        custom_css={
            ".ag-cell": {"font-size": "10px !important", "border-left": "2px solid black", "border-right": "2px solid black", "border-bottom": "2px solid black"},
            ".ag-header-cell-text, .ag-header-group-cell-label": {"font-size": "10px !important", "white-space": "normal", "line-height": "1.3"},
            ".vertical-header .ag-header-cell-label": {"writing-mode": "vertical-rl", "transform": "rotate(180deg)", "display": "flex", "align-items": "center", "justify-content": "center", "padding-bottom": "5px"},
        },
        key='aggrid_projetos_macae_v5'
    )
