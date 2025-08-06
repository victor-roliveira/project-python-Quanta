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

    # ## LÓGICA DE MAPEAMENTO POR NOMES ##
    # 1. Para cada tarefa, crie seu "caminho de nomes" completo.
    def get_name_path(path_list):
        return tuple(id_to_name_map.get('.'.join(path_list[:i+1]), '') for i in range(len(path_list)))

    df_escopo['name_path'] = df_escopo['hierarchy_path'].apply(get_name_path)

    # 2. Crie um dicionário para busca de status usando o caminho de nomes como chave.
    status_by_name_path = df_escopo.set_index('name_path')[['concluido', 'previsto']].to_dict('index')

    # Função de ordenação natural para garantir que '2' venha antes de '10'.
    def natural_sort_key(hid):
        return tuple(int(x) for x in hid.split('.'))

    # --- ETAPA 2: DEFINIR O MODELO DAS COLUNAS E CONSTRUIR A HIERARQUIA ---

    etapas_df = df[df['hierarchy_path'].apply(lambda p: len(p) == 2 and p[0] in projetos_principais_numeros)].copy()
    etapas_df['sort_key'] = etapas_df['hierarchy_id'].apply(natural_sort_key)
    etapas_df.sort_values(by='sort_key', inplace=True)
    etapas_para_mostrar = etapas_df[['hierarchy_id', 'tarefa']].to_records(index=False)

    if etapas_para_mostrar.size == 0:
        return st.warning("Nenhuma etapa (nível 2) encontrada para os projetos.")

    template_etapa_id = etapas_para_mostrar[0][0] # ID da primeira etapa

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
        # Se for uma tarefa "folha" (sem filhos), adicione seu caminho relativo de nomes
        if row['hierarchy_id'] not in df_escopo['hierarchy_path'].apply(lambda p: '.'.join(p[:-1]) if len(p) > 1 else None).unique():
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
            const concluido_percent = Math.round(concluido_val * 100);
            if (concluido_percent === 100) {
                eGui.style.backgroundColor = '#28a745'; eGui.style.color = 'white'; eGui.style.fontWeight = 'bold'; return '✔';
            } else if (concluido_percent < previsto_val) {
                eGui.style.backgroundColor = '#dc3545'; eGui.style.color = 'white'; return concluido_percent + '%';
            } else if (concluido_percent > previsto_val) {
                eGui.style.backgroundColor = '#ffffff'; eGui.style.color = 'black'; eGui.style.fontWeight = 'bold'; return concluido_percent + '%🔃';
            } else {
                eGui.style.backgroundColor = 'orange'; eGui.style.color = 'black'; eGui.style.fontWeight = 'bold'; return concluido_percent + '%🔄️';
            }
        }
    """)

    def build_nested_cols(parent_id, parent_name_path):
        children_defs = []
        child_ids = sorted(template_parent_child_map.get(parent_id, []), key=natural_sort_key)
        
        for child_id in child_ids:
            child_name = id_to_name_map.get(child_id, "N/A")
            current_name_path = parent_name_path + (child_name,)
            
            # O field da coluna será o caminho relativo de nomes, separado por um pipe
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
            # Células: fonte reduzida de 12px para 11px
            ".ag-cell": {"font-size": "10px !important", "border-left": "2px solid black", "border-right": "2px solid black", "border-bottom": "2px solid black"},
            
            # Cabeçalhos: fonte reduzida de 13px para 12px
            ".ag-header-cell-text, .ag-header-group-cell-label": {"font-size": "10px !important", "white-space": "normal", "line-height": "1.3"},
            
            # Estilos adicionais para cabeçalhos verticais (sem alteração)
            ".vertical-header .ag-header-cell-label": {"writing-mode": "vertical-rl", "transform": "rotate(180deg)", "display": "flex", "align-items": "center", "justify-content": "center", "padding-bottom": "5px"},
        },
        key='aggrid_projetos_macae_v5'
    )