import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, JsCode
import json

def mostrar_tabela_projetos_especificos_aggrid(df_original, filtro_nome=None):
    df = df_original.copy()
    df['tarefa'] = df['tarefa'].str.strip()

    # Adiciona o filtro de visualização
    view_selection = st.radio(
        "Selecione a Visualização:",
        ["Geral Detalhada", "Projetos"],
        horizontal=True,
        label_visibility="collapsed"
    )

    # --- ETAPA 1: PREPARAÇÃO DOS DADOS E IDENTIFICADORES ---

    df['hierarchy_path'] = df['hierarchy_path'].apply(lambda p: [str(i) for i in p] if isinstance(p, list) else [])
    df['hierarchy_id'] = df['hierarchy_path'].apply(lambda p: '.'.join(p))
    
    projetos_principais_numeros = {'3', '4', '5'}
    df_escopo = df[df['hierarchy_path'].apply(lambda p: len(p) > 0 and p[0] in projetos_principais_numeros)].copy()

    id_to_name_map = df.set_index('hierarchy_id')['tarefa'].to_dict()

    def get_name_path(path_list):
        return tuple(id_to_name_map.get('.'.join(path_list[:i+1]), '') for i in range(len(path_list)))

    df_escopo['name_path'] = df_escopo['hierarchy_path'].apply(get_name_path)

    status_by_name_path = df_escopo.set_index('name_path')[['concluido', 'previsto', 'terceiros', 'inicio']].to_dict('index')

    def natural_sort_key(hid):
        return tuple(int(x) for x in hid.split('.'))

    # --- ETAPA 2: PREPARAÇÃO DO DATAFRAME BASE (LINHAS) ---

    etapas_df = df[df['hierarchy_path'].apply(lambda p: len(p) == 2 and p[0] in projetos_principais_numeros)].copy()
    etapas_df['sort_key'] = etapas_df['hierarchy_id'].apply(natural_sort_key)
    etapas_df.sort_values(by='sort_key', inplace=True)
    etapas_para_mostrar = etapas_df[['hierarchy_id', 'tarefa']].to_records(index=False)

    if etapas_para_mostrar.size == 0:
        return st.warning("Nenhuma etapa (nível 2) encontrada para os projetos.")

    # --- RENDERERS JAVASCRIPT ---
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
            if (params.value == null || typeof params.value !== 'object') { eGui.style.backgroundColor = '#4d4d4d'; return ''; }
            const concluido_val = params.value.concluido || 0;
            const previsto_val = params.value.previsto || 0;
            const terceiros_val = params.value.terceiros || 0;
            const inicio_str = params.value.inicio;
            const concluido_percent = Math.round(concluido_val * 100);
            if (concluido_percent === 0) {
                if (terceiros_val > 0) {
                    if (inicio_str) {
                        const today = new Date(); today.setHours(0, 0, 0, 0);
                        const parts = inicio_str.split('/');
                        const startDate = new Date(parts[2], parts[1] - 1, parts[0]);
                        startDate.setHours(0, 0, 0, 0);
                        if (today > startDate) { eGui.style.color = 'red'; } else { eGui.style.color = 'white'; }
                    } else { c = 'white'; }
                    eGui.style.fontWeight = 'bold';
                    return '!';
                } else { eGui.style.color = 'white'; return '-'; }
            }
            const terceiros_indicator = terceiros_val > 0 ? '!' : '';
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
            } else {
                eGui.style.color = 'black'; eGui.style.fontWeight = 'bold';
                text_to_display = concluido_percent + '%';
            }
            return text_to_display + terceiros_indicator;
        }
    """)

    # --- ETAPA 3: LÓGICA CONDICIONAL PARA CONSTRUIR A TABELA ---

    column_defs = [
        {"headerName": "Etapa", "field": "Etapa", "pinned": "left", "width": 160, "cellStyle": {"fontWeight": "bold", "textAlign": "left"}},
        {"headerName": "Progresso", "field": "Progresso", "pinned": "left", "width": 120, "cellRenderer": barra_progress_renderer}
    ]
    
    grid_data = []

    if view_selection == "Projetos":
   
        projetos_structure = {
            "Plano de Trabalho": None,
            "Estudos Iniciais": ["Estudos Iniciais", "Visita Preliminar", "Topografia", "Planta Base da Área de Trabalho", "Sondagem", "Estudo Ambiental"],
            "Projetos Básicos": {
                "Arquitetura": ["Projetos Básicos", "Projeto Arquitetônico", "Paisagismo", "Urbanismo", "Envio Engenahria"],
                "Engenharia": ["Estrutural", "Hidrossanitário (Drenagem Reuso)", "PCI", "HVAC", "Gás", "Elétrico (CFRV Dados)", "Energia Renovável", "Orçamento"]
            },
            "Projetos Executivos": {
                "Arquitetura": ["Projetos Executivos", "Projeto Arquitetônico", "Paisagismo", "Urbanismo", "Entrega Orçamento"],
                "Engenharia": ["Estrutural", "Impermeabilização", "Hidrossanitário (Drenagem Reuso)", "PCI", "HVAC", "Gás", "Elétrico (CFRV Dados)", "Energia Renovável", "Orçamento"],
                "_folhas": ["Resumo do Projeto", "RE-Diretrizes para Operação e Manutenção"]
            },
            "Modelagem Econômica-Financeira": None,
            "Modelagem Jurídico Regulatório": None,
        }

        def build_cols_from_structure(structure):
            defs = []
            for header, content in structure.items():
                if content is None:
                    defs.append({"headerName": header, "field": header, "width": 80, "cellRenderer": cell_renderer_js})
                elif isinstance(content, list):
                    children = [{"headerName": name, "field": name, "width": 70, "cellRenderer": cell_renderer_js, "headerClass": "vertical-header"} for name in content]
                    defs.append({"headerName": header, "children": children})
                elif isinstance(content, dict):
                    sub_children = []
                    if "_folhas" in content:
                        sub_children.extend([{"headerName": name, "field": name, "width": 70, "cellRenderer": cell_renderer_js, "headerClass": "vertical-header"} for name in content["_folhas"]])
                    for sub_header, sub_content in content.items():
                        if sub_header != "_folhas":
                            sub_children.extend(build_cols_from_structure({sub_header: sub_content}))
                    defs.append({"headerName": header, "children": sub_children})
            return defs
        
        column_defs.extend(build_cols_from_structure(projetos_structure))

        # --- INÍCIO DA CORREÇÃO ---
        # Função recursiva para extrair TODOS os nomes de tarefas "folha" da estrutura.
        def get_all_leaf_tasks(structure):
            leaf_tasks = set()
            for key, value in structure.items():
                if value is None:
                    leaf_tasks.add(key)
                elif isinstance(value, list):
                    leaf_tasks.update(value)
                elif isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if sub_key == "_folhas":
                            leaf_tasks.update(sub_value)
                        elif isinstance(sub_value, list):
                            leaf_tasks.update(sub_value)
            return list(leaf_tasks)

        all_leaf_tasks = get_all_leaf_tasks(projetos_structure)
        # --- FIM DA CORREÇÃO ---
        
        for etapa_id, etapa_name in etapas_para_mostrar:
            row_data = {'Etapa': etapa_name}
            progress_info = df[df['hierarchy_id'] == etapa_id][['concluido', 'previsto']].iloc[0].to_dict()
            row_data['Progresso'] = json.dumps({'concluido': round(progress_info.get('concluido', 0) * 100), 'previsto': progress_info.get('previsto', 0)})
            
            for task_name in all_leaf_tasks:
                task_df = df_escopo[(df_escopo['tarefa'] == task_name) & (df_escopo['name_path'].apply(lambda p: p[1] == etapa_name if len(p) > 1 else False))]
                if not task_df.empty:
                    best_task = task_df.loc[task_df['concluido'].idxmax()]
                    row_data[task_name] = {'concluido': best_task['concluido'], 'previsto': best_task['previsto'], 'terceiros': best_task['terceiros'], 'inicio': best_task['inicio']}
                else:
                    row_data[task_name] = None
            grid_data.append(row_data)

    else: # Lógica "Geral Detalhada"
        template_etapa_id = etapas_para_mostrar[0][0]
        template_parent_child_map = {}
        template_descendants = df_escopo[df_escopo['hierarchy_path'].apply(lambda p: len(p) > 2 and '.'.join(p[:2]) == template_etapa_id)]
        leaf_name_paths_relative = []
        for _, row in template_descendants.iterrows():
            parent_id = '.'.join(row['hierarchy_path'][:-1])
            if parent_id not in template_parent_child_map:
                template_parent_child_map[parent_id] = []
            template_parent_child_map[parent_id].append(row['hierarchy_id'])
            is_leaf = row['hierarchy_id'] not in df_escopo['hierarchy_path'].apply(lambda p: '.'.join(p[:-1]) if len(p) > 1 else None).unique()
            if is_leaf:
                leaf_name_paths_relative.append(row['name_path'][2:])
        
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

        template_name_path_base = tuple(id_to_name_map.get('.'.join(template_etapa_id.split('.')[:i+1])) for i in range(2))
        column_defs.extend(build_nested_cols(template_etapa_id, template_name_path_base))

        etapa_progress_map = df[df['hierarchy_path'].apply(len) == 2].set_index('hierarchy_id')[['concluido', 'previsto']].to_dict('index')
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
        "defaultColDef": {"resizable": True, "sortable": False, "cellStyle": {"textAlign": "center"}, "suppressMenu": True},
        "domLayout": 'normal', "groupHeaderHeight": 45, "headerHeight": 80,
    }

    AgGrid(
        tabela_para_grid, gridOptions=gridOptions, height=700, allow_unsafe_jscode=True,
        enable_enterprise_modules=True,
        custom_css={
            ".ag-cell": {"font-size": "10px !important", "border-left": "2px solid black", "border-right": "2px solid black", "border-bottom": "2px solid black"},
            ".ag-header-cell-text, .ag-header-group-cell-label": {"font-size": "10px !important", "white-space": "normal", "line-height": "1.3"},
            ".vertical-header .ag-header-cell-label": {"writing-mode": "vertical-rl", "transform": "rotate(180deg)", "display": "flex", "align-items": "center", "justify-content": "center", "padding-bottom": "5px"},
            ".ag-header-cell-menu-button, .ag-header-group-cell-menu-button": {"display": "none !important"}
        },
        key=f"aggrid_projetos_macae_{view_selection}"
    )
