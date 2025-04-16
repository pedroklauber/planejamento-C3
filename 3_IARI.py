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

# Configuração para tela larga
st.set_page_config(layout="wide")

# Funções para persistência da data/hora
def get_last_update(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return f.read().strip()
    else:
        return "Nenhuma atualização realizada ainda."

def save_last_update(filename, timestamp):
    with open(filename, "w") as f:
        f.write(timestamp)

def abrir_e_atualizar():
    import pyautogui
    from selenium import webdriver

    navegador = webdriver.Edge()
    navegador.get("https://app.powerbi.com/groups/me/apps/3a3ed9f7-5758-4f52-97b1-8c3c1d1071ab/reports/c5da251e-0ece-4c02-9093-7a19047a6dda/ReportSectiond516ea33d2adcc6654bb?experience=power-bi")
    navegador.maximize_window()

    import time
    time.sleep(20)

    from selenium.webdriver.common.by import By

    # Clicar na barra de rolagem para aparecer o ícone de exportação
    navegador.find_element(By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[8]/transform/div/div[3]/div/div/div/div/div/div/h3').click()
    time.sleep(2)

    # Clicar no ícone de exportação
    navegador.find_element(By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[8]/transform/div/visual-container-header/div/div/div/visual-container-options-menu/visual-header-item-container/div/button').click()
    time.sleep(2)

    # Escolher exportação de dados
    navegador.find_element(By.XPATH, '//*[@id="6"]').click()
    time.sleep(2)

    # Escolher dados resumidos
    navegador.find_element(By.XPATH, '//*[@id="pbi-radio-button-1"]/label/section').click()
    time.sleep(2)

    # Escolher botão CSV
    navegador.find_element(By.XPATH, '//*[@id="$pbi-dropdown-0"]/pbi-dropdown-trigger/p').click()
    time.sleep(2)

    # Escolher botão CSV 30k
    pyautogui.click(x=744, y=901)
    time.sleep(2)

    # Apertar botão verde
    pyautogui.click(x=1151, y=910)
    time.sleep(3)

    # Apertar botão salvar planilha
    pyautogui.click(x=1792, y=71)
    time.sleep(3)
    pyautogui.click(x=1792, y=71)
    time.sleep(3)
    pyautogui.click(x=1551, y=198)
    time.sleep(3)

    # Digitar o caminho e salvar o arquivo CSV
    import pyautogui as caminho
    caminho.typewrite('C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\IARI.csv')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.press('left')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(5)

    # Modificar colunas do arquivo IARI
    df_iari = pd.read_csv('C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\IARI.csv')
    df_iari['Medida'] = df_iari['Medida'].apply(lambda x: str(x).split('-')[0])
    df_iari.rename(columns={'Medida': 'NOTA'}, inplace=True)
    df_iari.to_csv('C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\IARI.csv', index=False)

    time.sleep(10)

    # Atualizar planilha DATABASE
    import xlwings as xw
    import time
    import pyautogui as rs

    # Abrir o Executar
    rs.hotkey('win', 'r')
    time.sleep(2)
    rs.typewrite("C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\database_indicadores.xlsx")
    time.sleep(2)
    rs.press('enter')
    time.sleep(8)

    caminho_excel = "C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\database_indicadores.xlsx"
    wb = xw.Book(caminho_excel)

    # Atualizar a aba "IARI"
    aba_especifica = "IARI"
    for sheet in wb.sheets:
        if sheet.name == aba_especifica:
            sheet.api.ListObjects(1).QueryTable.Refresh()

    time.sleep(10)
    wb.save()
    wb.close()

def processar_dados():
    file_path = "C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\database_indicadores.xlsx"
    
    # Verificar se a aba "IARI" existe
    xls = pd.ExcelFile(file_path)
    if "IARI" not in xls.sheet_names:
        st.error(f"A aba 'IARI' não foi encontrada. Abas disponíveis: {xls.sheet_names}")
        st.stop()

    # Carregar a aba "IARI"
    df_iari = pd.read_excel(file_path, sheet_name="IARI")

    # Selecionar as colunas necessárias
    colunas_necessarias = ['NOTA', 'ORDEM', 'Texto da Nota', 'Cód', 'Data Vencimento', 'STATUS PRIORIZA', 'PROGRAMACAO']
    for col in colunas_necessarias:
        if col not in df_iari.columns:
            st.error(f"A coluna '{col}' não foi encontrada no arquivo.")
            st.stop()

    df_resumo = df_iari[colunas_necessarias].copy()

    # Converter 'Data Vencimento' para datetime
    df_resumo['Data Vencimento'] = pd.to_datetime(df_resumo['Data Vencimento'], format='%d/%m/%Y', errors='coerce')

    df_resumo = df_resumo.dropna(subset=['NOTA'])
    df_resumo['NOTA'] = pd.to_numeric(df_resumo['NOTA'], errors='coerce').fillna(0).astype(int)

    # Criar coluna para agrupamento por mês (MM/YYYY)
    df_resumo['Mês'] = df_resumo['Data Vencimento'].dt.strftime("%m/%Y")

    # Ordenar a tabela por Data Vencimento
    df_resumo = df_resumo.sort_values(by='Data Vencimento', ascending=True)
    df_resumo['Data Vencimento'] = df_resumo['Data Vencimento'].dt.strftime("%d/%m/%Y")

    st.title("📊 Resumo de IARI")
    st.header("Tabela única agrupada por mês e ordenada por Data Vencimento")
    st.dataframe(df_resumo, use_container_width=True)

def main():
    st.title("IARI")
    
    # Exibir registros persistentes de atualização
    last_update_db = get_last_update("last_update_iari_db.txt")
    st.write("Última atualização do banco de dados:", last_update_db)
    last_update_proc = get_last_update("last_update_iari_proc.txt")
    st.write("Última atualização do processamento:", last_update_proc)
    
    if st.button("Abrir Power BI e Atualizar Banco de Dados"):
        abrir_e_atualizar()
        st.success("Dados atualizados com sucesso!")
        notification.notify(
            title="Atualização Concluída", 
            message="✅ Banco de dados atualizado.", 
            timeout=10
        )
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        save_last_update("last_update_iari_db.txt", now)
        st.write("Última atualização do banco de dados:", now)

    if st.button("Processar Dados"):
        processar_dados()
        st.success("Dados processados com sucesso!")
        notification.notify(
            title="Atualização Concluída", 
            message="✅ Dados processados.", 
            timeout=10
        )
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        save_last_update("last_update_iari_proc.txt", now)
        st.write("Última atualização do processamento:", now)

if __name__ == "__main__":
    main()
