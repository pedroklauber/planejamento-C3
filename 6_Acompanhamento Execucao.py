import streamlit as st
import time
import pandas as pd
import pyautogui
import xlwings as xw
import os
from selenium import webdriver
from selenium.webdriver.common.by import By

# Configurar a página
st.set_page_config(layout="wide", page_title="Gerenciamento Dados")

# ---------------------- Configuração Global ----------------------
centers = {
    "TECINREF": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_TECINREF.html",
    "TECINTRE": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_TECINTRE.html",
    "ELETMONT": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_ELETMONT.html",
    "MONTAREF": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_MONTAREF.html",
    "ISOLADOR": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_ISOLADOR.html",
    "PINTINDU": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_PINTINDU.html",
    "PEDRCONT": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_PEDRCONT.html",
    "AJUDLIMP": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_AJUDLIMP.html",
    "MECANROT": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_MECANROT.html",
    "MECAUSIN": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_MECAUSIN.html",
    "OPERGUIN": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_OPERGUIN.html",
    "CALDIUTL": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_CALDIUTL.html",
    "SOLDCOT1": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_SOLDCOT1.html",
    "JATICOT1": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_JATICOT1.html",
    "TECNINSP": r"c:\Users\RSKG\PETROBRAS\Serviços Integrados de Rotina - Documentos\Rotina RECAP\Acompanhamento_Execução_TECNINSP.html"
}

# ---------------------- Função: Atualiza Apontamentos ----------------------
def update_apontamentos() -> str:
    try:
        navegador = webdriver.Edge()
        navegador.get("https://app.powerbi.com/groups/me/apps/7d1d1b76-89e3-44c6-8bac-36130117cfb9/reports/3de2c3c5-7020-463f-8b94-0b45af1798d8/ReportSection5d9a748a7d91d81b7a93?ctid=5b6f6241-9a57-4be4-8e50-1dfa72e79a57&experience=power-bi")
        navegador.maximize_window()
        time.sleep(30)
        navegador.find_element(By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[15]/transform/div/div[3]/div/div/visual-modern/div/div/div[2]/div[4]').click()
        time.sleep(2)
        navegador.find_element(By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[15]/transform/div/visual-container-header/div/div/div/visual-container-options-menu/visual-header-item-container/div/button').click()
        time.sleep(2)
        navegador.find_element(By.XPATH, '//*[@id="6"]').click()
        time.sleep(2)
        navegador.find_element(By.XPATH, '//*[@id="pbi-radio-button-1"]/label/section').click()
        time.sleep(2)
        navegador.find_element(By.XPATH, '//*[@id="$pbi-dropdown-0"]/pbi-dropdown-trigger/p').click()
        time.sleep(2)
        navegador.find_element(By.XPATH, '/html/body/div[2]/div[6]/div/pbi-dropdown-overlay/div/div/pbi-dropdown-item[2]/div').click()
        time.sleep(2)
        navegador.find_element(By.XPATH, '/html/body/div[2]/div[4]/div/mat-dialog-container/div/div/export-data-dialog/mat-dialog-actions/button[1]').click()
        time.sleep(4)
        pyautogui.moveTo(1551, 198)
        pyautogui.click(button='left')
        time.sleep(2)
        pyautogui.typewrite(r'C:\Users\RSKG\OneDrive - PETROBRAS\C3\Banco de dados\apontamentos.csv')
        time.sleep(2)
        pyautogui.press('enter')
        time.sleep(2)
        pyautogui.press('left')
        time.sleep(2)
        pyautogui.press('enter')
        time.sleep(10)
        navegador.quit()
        return "Atualização dos apontamentos concluída com sucesso!"
    except Exception as e:
        return f"Erro ao atualizar apontamentos: {e}"

# ---------------------- Função: Gera HTML para um Centro ----------------------
def generate_html(centro: str, output_file: str) -> str:
    try:
        file_path = r"C:\Users\RSKG\OneDrive - PETROBRAS\C3\Banco de dados\database_indicadores.xlsx"
        sheet_name = "nivelamento_trilha"
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        
        # Padroniza a coluna de centro para "CenTrabOperação"
        if "CenTrabOperação" not in df.columns and "Centro de Trabalho" in df.columns:
            df = df.rename(columns={"Centro de Trabalho": "CenTrabOperação"})
        if "CenTrabOperação" not in df.columns:
            raise KeyError("Coluna de centro não encontrada em 'nivelamento_trilha'.")
        center_col = "CenTrabOperação"
        
        df_centro = df[df[center_col] == centro]
        ordens = df_centro["Ordem"].unique()
        df_filtrado = df[df["Ordem"].isin(ordens)]
        colunas = ["Rank", "GPM", "Ordem", "Operação", "TxtDesc.Oper.", center_col,
                   "Trabalho", "Apontamentos", "DATA SOLICITAÇÃO PT", "DATA ATRE"]
        df_formatado = df_filtrado[colunas].sort_values(by=["Rank", "Ordem", "Operação"])
        
        # Converte datas e normaliza (removendo hora)
        df_formatado["DATA SOLICITAÇÃO PT"] = pd.to_datetime(df_formatado["DATA SOLICITAÇÃO PT"], errors='coerce').dt.normalize()
        df_formatado["DATA ATRE"] = pd.to_datetime(df_formatado["DATA ATRE"], errors='coerce').dt.normalize()
        today = pd.Timestamp("today").normalize()
        mask = (df_formatado["DATA SOLICITAÇÃO PT"] == today) | (df_formatado["DATA ATRE"] == today)
        df_today = df_formatado[mask]
        total_trabalho = pd.to_numeric(df_today["Trabalho"], errors='coerce').sum()
        
        html_styled = f"""
<!DOCTYPE html>
<html>
<head>
<div id="ww_ad5b2a2941688" v='1.3' loc='id' a='{{"t":"responsive","lang":"pt","sl_lpl":1,"ids":["wl4890"],"font":"Arial","sl_ics":"one_a","sl_sot":"celsius","cl_bkg":"#FFFFFF","cl_font":"#000000","cl_cloud":"#d4d4d4","cl_persp":"#2196F3","cl_sun":"#FFC107","cl_moon":"#FFC107","cl_thund":"#FF5722","sl_tof":"5","cl_odd":"#0000000a"}}'>
Fonte de dados meteorológicos: <a href="https://wetterlang.de" id="ww_ad5b2a2941688_u" target="_blank">Wettervorhersage 30 tage</a>
</div>
<script async src="https://app3.weatherwidget.org/js/?id=ww_ad5b2a2941688"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; font-size: 12px; background-color: #f8f9fa; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 12px; }}
        th, td {{ border: 1px solid black; padding: 6px; text-align: left; }}
        th {{ background-color: #212529; color: white; position: sticky; top: 0; z-index: 2; }}
        .order-group {{ background-color: #000080; color: white; font-weight: bold; text-align: left; font-size: 14px; }}
        .montaref {{ background-color: #ADD8E6; color: black; font-weight: bold; text-align: left; }}
        .apontado {{ background-color: #DCDCDC !important; color: DarkGray !important; font-weight: bold; text-align: left; }}
    </style>
</head>
<body>
    <h2 style="text-align:center; color:#212529;">Ordens - {centro}</h2>
    <table>
        <tr>
            <th>Rank</th>
            <th>GPM</th>
            <th>Ordem</th>
            <th>Operação</th>
            <th>Descrição</th>
            <th>{center_col}</th>
            <th>Trabalho</th>
            <th>Apontamentos</th>
            <th>DATA SOLICITAÇÃO PT</th>
            <th>DATA ATRE</th>
        </tr>
"""
        current_order = None
        for _, row in df_formatado.iterrows():
            if row["Ordem"] != current_order:
                html_styled += f'<tr class="order-group"><td colspan="10">Ordem {row["Ordem"]}</td></tr>'
                current_order = row["Ordem"]
            is_apontado = isinstance(row["Apontamentos"], str) and "apontado" in row["Apontamentos"].lower()
            is_center = row[center_col] == centro
            row_class = "apontado" if is_apontado else ("montaref" if is_center else "")
            center_val = f'<span class="montaref">{row[center_col]}</span>' if is_center else row[center_col]
            html_styled += f"""
        <tr class="{row_class}">
            <td>{row["Rank"]}</td>
            <td>{row["GPM"]}</td>
            <td>{row["Ordem"]}</td>
            <td>{row["Operação"]}</td>
            <td>{row["TxtDesc.Oper."]}</td>
            <td>{center_val}</td>
            <td>{row["Trabalho"]}</td>
            <td>{row["Apontamentos"]}</td>
            <td>{row["DATA SOLICITAÇÃO PT"]}</td>
            <td>{row["DATA ATRE"]}</td>
        </tr>
        """
        html_styled += f"""
    </table>
    <p style="font-weight: bold; font-size: 14px;">Total de Trabalho Programado para Hoje: {total_trabalho}</p>
</body>
</html>
"""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_styled)
        return f"Arquivo HTML gerado com sucesso: {output_file}"
    except Exception as e:
        return f"Erro na geração do HTML para {centro}: {e}"

# ---------------------- Função: Gera Todos os HTMLs ----------------------
def generate_all_html() -> str:
    messages = []
    for centro, output_file in centers.items():
        msg = generate_html(centro, output_file)
        messages.append(msg)
    return "\n".join(messages)

# ---------------------- Função: Abre o arquivo HTML ----------------------
def open_html_file(file_path: str) -> str:
    try:
        if os.path.exists(file_path):
            os.startfile(file_path)
            return f"Arquivo {file_path} aberto com sucesso."
        else:
            return "Arquivo HTML não encontrado. Atualize os dados para gerar o HTML."
    except Exception as e:
        return f"Erro ao abrir o arquivo HTML: {e}"

# ---------------------- Função: Lê o conteúdo do HTML (para download) ----------------------
def get_html_content(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Erro ao ler o arquivo HTML: {e}"

# ---------------------- Função: Gera o Resumo dos Centros de Trabalho para Hoje ----------------------
def get_summary() -> pd.DataFrame:
    try:
        file_path = r"C:\Users\RSKG\OneDrive - PETROBRAS\C3\Banco de dados\database_indicadores.xlsx"
        
        # Processa a aba "nivelamento_trilha"
        df_nivel = pd.read_excel(file_path, sheet_name="nivelamento_trilha")
        # Padroniza a coluna de centro para "CenTrabOperação"
        if "CenTrabOperação" not in df_nivel.columns and "Centro de Trabalho" in df_nivel.columns:
            df_nivel = df_nivel.rename(columns={"Centro de Trabalho": "CenTrabOperação"})
        if "CenTrabOperação" not in df_nivel.columns:
            raise KeyError("Nenhuma coluna de centro encontrada na aba 'nivelamento_trilha'.")
        center_col = "CenTrabOperação"
        
        df_nivel["DATA SOLICITAÇÃO PT"] = pd.to_datetime(df_nivel["DATA SOLICITAÇÃO PT"], errors='coerce').dt.normalize()
        df_nivel["DATA ATRE"] = pd.to_datetime(df_nivel["DATA ATRE"], errors='coerce').dt.normalize()
        today = pd.Timestamp("today").normalize()
        
        df_pt = df_nivel[df_nivel["DATA SOLICITAÇÃO PT"] == today]
        summary_pt = df_pt.groupby(center_col)["Trabalho"].sum().reset_index().rename(columns={"Trabalho": "Total PT"})
        df_atre = df_nivel[df_nivel["DATA ATRE"] == today]
        summary_atre = df_atre.groupby(center_col)["Trabalho"].sum().reset_index().rename(columns={"Trabalho": "Total ATRE"})
        
        summary = pd.merge(summary_pt, summary_atre, on=center_col, how="outer").fillna(0)
        
        # Processa a aba "Cargas Semanais"
        df_cargas = pd.read_excel(file_path, sheet_name="Cargas Semanais")
        if "CenTrabOperação" not in df_cargas.columns and "Centro de Trabalho" in df_cargas.columns:
            df_cargas = df_cargas.rename(columns={"Centro de Trabalho": "CenTrabOperação"})
        if "CenTrabOperação" not in df_cargas.columns:
            raise KeyError("Nenhuma coluna de centro encontrada na aba 'Cargas Semanais'.")
        center_col_cargas = "CenTrabOperação"
        
        summary_occup = df_cargas.groupby(center_col_cargas)["Ocupação diária"].sum().reset_index().rename(
            columns={"Ocupação diária": "Ocupação Diária Total"})
        summary_nec = df_cargas.groupby(center_col_cargas)["Necessidade"].sum().reset_index().rename(
            columns={"Necessidade": "Necessidade Total"})
        summary_carga = pd.merge(summary_occup, summary_nec, on=center_col_cargas, how="outer").fillna(0)
        
        # Mescla os resumos utilizando a coluna padronizada
        final_summary = pd.merge(summary, summary_carga, on=center_col, how="outer").fillna(0)
        return final_summary
    except Exception as e:
        st.error(f"Erro ao gerar o resumo: {e}")
        return pd.DataFrame()

# ---------------------- Função: Atualiza os Dados e Gera os HTMLs ----------------------
def update_planilhas() -> str:
    try:
        csv_file = r"C:\Users\RSKG\OneDrive - PETROBRAS\C3\Banco de dados\PT_SOLICITADAS_DATA_BASE.csv"
        df = pd.read_csv(csv_file)
        df_expanded = df.assign(**{"Operações PT/PTT": df["Operações PT/PTT"].astype(str).str.split(", ")}).explode("Operações PT/PTT")
        colunas_desejadas = [
            "Nº OM/Diagr. de Rede", 
            "Operações PT/PTT", 
            "Data de Priorização", 
            "Descrição PT/PTT", 
            "Requisitante"
        ]
        df_result = df_expanded[colunas_desejadas]
        df_result["Operações PT/PTT"] = pd.to_numeric(df_result["Operações PT/PTT"].astype(str).str.strip(), errors='coerce').fillna(0).astype(int)
        output_csv = r"C:\Users\RSKG\OneDrive - PETROBRAS\C3\Banco de dados\solicitacoes_PT_processadas.csv"
        df_result.to_csv(output_csv, index=False, sep=';', encoding='utf-8')
        
        import pyautogui as rs
        rs.hotkey('win', 'r')
        time.sleep(2)
        rs.typewrite(r"C:\Users\RSKG\OneDrive - PETROBRAS\C3\Banco de dados\database_indicadores.xlsx")
        time.sleep(2)
        rs.press('enter')
        time.sleep(8)
        
        caminho_excel = r"C:\Users\RSKG\OneDrive - PETROBRAS\C3\Banco de dados\database_indicadores.xlsx"
        wb = xw.Book(caminho_excel)
        for sheet in wb.sheets:
            if sheet.name == "solicitacoes_PT_processadas":
                sheet.api.ListObjects(1).QueryTable.Refresh()
        for sheet in wb.sheets:
            if sheet.name == "atre_programacao":
                sheet.api.ListObjects(1).QueryTable.Refresh()
        for sheet in wb.sheets:
            if sheet.name == "apontamentos_trilha":
                sheet.api.ListObjects(1).QueryTable.Refresh()
        time.sleep(10)
        wb.save()
        wb.close()
        generate_all_html()
        return "Atualização dos dados e geração dos HTML concluída com sucesso!"
    except Exception as e:
        return f"Erro na atualização dos dados: {e}"

# ---------------------- Streamlit App ----------------------
st.title("Rotina de Atualização e Exportação de Dados")
st.text("Antes, atualizar a planilha de solicitação de PTs no Power Bi Petrobras, salvando como solicitação de PT database. ")

st.header("1. Atualização dos Apontamentos")
if st.button("Atualizar Apontamentos"):
    msg = update_apontamentos()
    st.success(msg)

st.header("2. Atualização dos Dados e Geração Automática dos HTML")
if st.button("Atualizar Dados"):
    msg = update_planilhas()
    st.success(msg)

st.header("Resumo dos Centros de Trabalho para Hoje")
summary_df = get_summary()
if not summary_df.empty:
    # Cria a coluna "Capacidade (%)" dividindo Total PT por Ocupação Diária Total (evitando divisão por zero)
    summary_df['Capacidade (%)'] = summary_df.apply(
        lambda row: (row['Total PT'] / row['Ocupação Diária Total'] * 100) if row['Ocupação Diária Total'] != 0 else 0, axis=1
    ).round(2)
    
    st.dataframe(summary_df)
    
    csv_summary = summary_df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download Resumo CSV",
                       data=csv_summary,
                       file_name="Resumo_Centros.csv",
                       mime="text/csv")
else:
    st.info("Não há dados de hoje para exibir no resumo.")

st.header("3. Ações sobre os Arquivos HTML")
st.write("Utilize as opções abaixo para abrir ou fazer download dos arquivos HTML gerados:")

for centro, output_file in centers.items():
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"Abrir HTML {centro}"):
            open_msg = open_html_file(output_file)
            if "sucesso" in open_msg:
                st.success(open_msg)
            else:
                st.error(open_msg)
    with col2:
        if os.path.exists(output_file):
            html_content = get_html_content(output_file)
            st.download_button(label=f"Download HTML {centro}",
                               data=html_content,
                               file_name=os.path.basename(output_file),
                               mime="text/html")
        else:
            st.info(f"Arquivo {centro} não encontrado. Atualize os dados para gerar o HTML.")




        