import streamlit as st
import time
import pandas as pd
import pyautogui
import xlwings as xw
from selenium import webdriver
from selenium.webdriver.common.by import By
from plyer import notification
from datetime import datetime
import os
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Gerenciamento de Ordens")

# ======================================
# Funções para persistência de data/hora
# ======================================
def get_last_update(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return f.read().strip()
    else:
        return "Nenhuma atualização realizada ainda."

def save_last_update(filename, timestamp):
    with open(filename, "w") as f:
        f.write(timestamp)

# ============================
# Funcionalidade VAZAMENTOS
# ============================
def abrir_e_atualizar():
    navegador = webdriver.Edge()
    navegador.get("https://app.powerbi.com/groups/me/apps/3a3ed9f7-5758-4f52-97b1-8c3c1d1071ab/reports/c18fe9b6-0697-48d7-b4df-867f6b94fd47/ReportSection0ca367d03101440b3077?experience=power-bi")
    navegador.maximize_window()
    time.sleep(30)

    navegador.find_element(By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[9]/transform/div/div[3]/div/div/visual-modern/div/div/div[2]/div[4]').click()
    time.sleep(2)
    navegador.find_element(By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[9]/transform/div/visual-container-header/div/div/div/visual-container-options-menu/visual-header-item-container/div/button').click()
    time.sleep(2)
    navegador.find_element(By.XPATH, '//*[@id="6"]').click()
    time.sleep(2)
    navegador.find_element(By.XPATH, '//*[@id="pbi-radio-button-1"]/label/section').click()
    time.sleep(2)
    navegador.find_element(By.XPATH, '//*[@id="$pbi-dropdown-0"]/pbi-dropdown-trigger/p').click()
    time.sleep(2)
    pyautogui.click(x=744, y=901)
    time.sleep(2)
    pyautogui.click(x=1151, y=910)
    time.sleep(3)
    pyautogui.click(x=1511, y=198)
    time.sleep(3)
    pyautogui.typewrite('C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\vazamentos.csv')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.press('left')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(10)

    rs = pyautogui
    rs.hotkey('win', 'r')
    time.sleep(2)
    rs.typewrite("C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\database_indicadores.xlsx")
    time.sleep(2)
    rs.press('enter')
    time.sleep(8)

    caminho_excel = "C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\database_indicadores.xlsx"
    wb = xw.Book(caminho_excel)
    aba_especifica = "VAZAMENTOS"
    for sheet in wb.sheets:
        if sheet.name == aba_especifica:
            sheet.api.ListObjects(1).QueryTable.Refresh()
    time.sleep(10)
    wb.save()
    wb.close()

def processar_dados(fluido_selecionado):
    file_path = "C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\database_indicadores.xlsx"
    xls = pd.ExcelFile(file_path)
    if "VAZAMENTOS" not in xls.sheet_names:
        st.error(f"A aba 'VAZAMENTOS' não foi encontrada. Abas disponíveis: {xls.sheet_names}")
        st.stop()

    df_vazamentos = pd.read_excel(file_path, sheet_name="VAZAMENTOS")
    colunas_necessarias = ['ORDEM', 'NOTA', 'TEXTO_BREVE', 'FLUIDO', 'GPM', 'STATUS PRIORIZA', 'PROGRAMACAO', '% Avanço', 'Info', 'Modificação']
    for col in colunas_necessarias:
        if col not in df_vazamentos.columns:
            st.error(f"A coluna '{col}' não foi encontrada no arquivo.")
            st.stop()

    df_resumo_vazamentos = df_vazamentos[colunas_necessarias]
    df_resumo_vazamentos = df_resumo_vazamentos.dropna(subset=['NOTA'])
    df_resumo_vazamentos['NOTA'] = pd.to_numeric(df_resumo_vazamentos['NOTA'], errors='coerce').fillna(0).astype(int)
    df_resumo_vazamentos = df_resumo_vazamentos.sort_values(by='STATUS PRIORIZA', ascending=True)

    df_filtrado = df_resumo_vazamentos[df_resumo_vazamentos['FLUIDO'].isin(fluido_selecionado)]

    resumo_quantitativo = df_filtrado['STATUS PRIORIZA'].value_counts().reset_index()
    resumo_quantitativo.columns = ['STATUS PRIORIZA', 'TOTAL']
    resumo_quantitativo = pd.concat([
        resumo_quantitativo,
        pd.DataFrame({'STATUS PRIORIZA': ['TOTAL'], 'TOTAL': [resumo_quantitativo['TOTAL'].sum()]})
    ], ignore_index=True)

    filtro_vapor_condensado = df_filtrado[df_filtrado['FLUIDO'].isin(['VAPOR', 'CONDENSADO'])]
    resumo_quantitativo_vapor_condensado = filtro_vapor_condensado['STATUS PRIORIZA'].value_counts().reset_index()
    resumo_quantitativo_vapor_condensado.columns = ['STATUS PRIORIZA', 'TOTAL']
    resumo_quantitativo_vapor_condensado = pd.concat([
        resumo_quantitativo_vapor_condensado,
        pd.DataFrame({'STATUS PRIORIZA': ['TOTAL'], 'TOTAL': [resumo_quantitativo_vapor_condensado['TOTAL'].sum()]})
    ], ignore_index=True)

    st.title("📊 Resumo de Vazamentos por Status Priorizado")
    st.header("Resumo Quantitativo Geral")
    st.dataframe(resumo_quantitativo, use_container_width=True)
    st.header("Resumo Quantitativo - Apenas Vapor e Condensado")
    st.dataframe(resumo_quantitativo_vapor_condensado, use_container_width=True)
    st.header("📌 Detalhamento por STATUS PRIORIZA")
    for status, grupo in df_filtrado.groupby('STATUS PRIORIZA'):
        st.subheader(f"Status: {status}")
        st.dataframe(grupo, use_container_width=True)

    # Salvar histórico CSV
    historico_path = "C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\historico_resumo_vazamentos.csv"
    hoje = datetime.now().strftime("%Y-%m-%d")

    def salvar_historico(df_resumo, tipo):
        df_resumo["Data"] = hoje
        df_resumo["Tipo"] = tipo
        df_resumo = df_resumo[["Data", "Tipo", "STATUS PRIORIZA", "TOTAL"]]

        if os.path.exists(historico_path):
            df_hist = pd.read_csv(historico_path)
            df_hist = df_hist[~((df_hist["Data"] == hoje) & (df_hist["Tipo"] == tipo))]
            df_hist = pd.concat([df_hist, df_resumo], ignore_index=True)
        else:
            df_hist = df_resumo

        df_hist.to_csv(historico_path, index=False)

    salvar_historico(resumo_quantitativo.copy(), tipo="Geral")
    salvar_historico(resumo_quantitativo_vapor_condensado.copy(), tipo="Vapor/Condensado")

def gerar_grafico_historico_por_semana():
    historico_path = "C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\historico_resumo_vazamentos.csv"

    if not os.path.exists(historico_path):
        st.error("Arquivo de histórico não encontrado.")
        return

    df_hist = pd.read_csv(historico_path)
    df_hist["Data"] = pd.to_datetime(df_hist["Data"], format="%Y-%m-%d")
    df_hist["Semana"] = df_hist["Data"].apply(lambda x: f"{x.isocalendar().week:02}.{x.isocalendar().year}")
    tipos = df_hist["Tipo"].unique()

    for tipo in tipos:
        df_tipo = df_hist[df_hist["Tipo"] == tipo]
        pivot = df_tipo.pivot_table(index="Semana", columns="STATUS PRIORIZA", values="TOTAL", aggfunc="sum").fillna(0)
        pivot = pivot.sort_index()

        st.subheader(f"📈 Histórico Semanal - {tipo}")
        fig, ax = plt.subplots(figsize=(10, 5))
        for coluna in pivot.columns:
            ax.plot(pivot.index, pivot[coluna], marker='o', label=coluna)
        ax.set_title(f"Resumo por STATUS PRIORIZA ({tipo})")
        ax.set_xlabel("Semana (SS.ANO)")
        ax.set_ylabel("Total")
        ax.legend()
        ax.grid(True)
        plt.xticks(rotation=45)
        st.pyplot(fig)

def main_vazamentos():
    st.title("VAZAMENTOS")
    st.text("⛔Atualizar a aba database_indicadore - aba: BD_SAP_NOTAS E ORDENS. Exportar dados do SAP//IW28 - NOTAS ABERTAS E EM PROCESSAMENTO -Z1 VARIANTE")
    last_update_db = get_last_update("last_update_vazamentos_db.txt")
    st.write("Última atualização - Banco de Dados:", last_update_db)
    last_update_proc = get_last_update("last_update_vazamentos_proc.txt")
    st.write("Última atualização - Processamento:", last_update_proc)

    file_path = "C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\database_indicadores.xlsx"
    try:
        xls = pd.ExcelFile(file_path)
        if "VAZAMENTOS" not in xls.sheet_names:
            st.error(f"A aba 'VAZAMENTOS' não foi encontrada. Abas disponíveis: {xls.sheet_names}")
            st.stop()
        df_vazamentos = pd.read_excel(file_path, sheet_name="VAZAMENTOS")
        opcoes_fluido = st.multiselect("Selecione os valores de FLUIDO:", options=df_vazamentos['FLUIDO'].unique(), default=df_vazamentos['FLUIDO'].unique())
    except Exception as e:
        st.error("Erro ao carregar os dados de vazamentos: " + str(e))
        opcoes_fluido = []

    if st.button("Processar Dados"):
        processar_dados(fluido_selecionado=opcoes_fluido)
        st.success("Dados processados com sucesso!")
        notification.notify(title="Atualização Concluída", message="✅ Apontamentos atualizados.", timeout=10)
        last_update_proc = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        save_last_update("last_update_vazamentos_proc.txt", last_update_proc)
        st.write("Última atualização - Processamento:", last_update_proc)

    if st.button("Abrir Power BI e Atualizar Banco de Dados"):
        abrir_e_atualizar()
        st.success("Dados atualizados com sucesso!")
        notification.notify(title="Atualização Concluída", message="✅ Banco de dados atualizado.", timeout=10)
        last_update_db = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        save_last_update("last_update_vazamentos_db.txt", last_update_db)
        st.write("Última atualização - Banco de Dados:", last_update_db)

    if st.button("📈 Ver Gráficos Semanais"):
        gerar_grafico_historico_por_semana()

# ======================================
# Banco de Dados Info - Atualização Info
# ======================================
CSV_FILE = "C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\ordens_status.csv"
EXCEL_FILE = "C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\database_indicadores.xlsx"
SHEET_NAME = "prioriza"

if not os.path.exists(CSV_FILE):
    df_temp = pd.DataFrame(columns=["Ordem", "Informações", "Serviço", "Última Atualização", "Categoria"])
    df_temp.to_csv(CSV_FILE, index=False)

def load_data():
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

st.sidebar.header("Atribuir Ordem")
ordem = st.sidebar.text_input("Número da Ordem")

if ordem:
    df = load_data()
    if ordem in df["Ordem"].astype(str).values:
        index = df[df["Ordem"].astype(str) == ordem].index[0]
        info_atual = df.at[index, "Informações"]
        servico_atual = df.at[index, "Serviço"]
        categoria_atual = df.at[index, "Categoria"] if "Categoria" in df.columns else ""
    else:
        info_atual = ""
        servico_atual = ""
        categoria_atual = ""

    nova_info = st.sidebar.text_area("Informações", value=info_atual, key="info_input")
    servico_manual = st.sidebar.text_input("Serviço", value=servico_atual, key="servico_input")
    categoria_manual = st.sidebar.text_input("Categoria", value=categoria_atual, key="categoria_input")

    if st.sidebar.button("Salvar Atualização"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if ordem in df["Ordem"].astype(str).values:
            index = df[df["Ordem"].astype(str) == ordem].index[0]
            df.at[index, "Informações"] = nova_info
            df.at[index, "Serviço"] = servico_manual
            df.at[index, "Última Atualização"] = now
            df.at[index, "Categoria"] = categoria_manual
        else:
            new_row = pd.DataFrame({
                "Ordem": [ordem],
                "Informações": [nova_info],
                "Serviço": [servico_manual],
                "Última Atualização": [now],
                "Categoria": [categoria_manual]
            })
            df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.sidebar.success("Ordem atualizada com sucesso!")

    if st.sidebar.button("Apagar Ordem"):
        df = load_data()
        if ordem in df["Ordem"].astype(str).values:
            df = df[df["Ordem"].astype(str) != ordem]
            save_data(df)
            st.sidebar.success("Ordem apagada com sucesso!")
        else:
            st.sidebar.error("Ordem não encontrada para apagar.")

# ======================================
# Menu principal
# ======================================
nav_option = st.sidebar.selectbox("Navegação Rápida", 
                                  ["Banco de Dados Info", "Vazamentos"], index=1)

if nav_option == "Banco de Dados Info":
    st.title("Banco de Dados de Ordens")
    df_display = load_data()
    if "Categoria" not in df_display.columns:
        df_display["Categoria"] = "não categorizado"
    else:
        df_display["Categoria"] = df_display["Categoria"].fillna("").replace("", "não categorizado")

    for categoria, grupo in df_display.groupby("Categoria"):
        st.subheader(f"Categoria: {categoria}")
        st.dataframe(grupo, use_container_width=True)

elif nav_option == "Vazamentos":
    main_vazamentos()
