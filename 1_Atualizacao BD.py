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




# Configurar a página
st.set_page_config(layout="wide", page_title="Gerenciamento Dados")

# Funções para manipulação dos registros de atualização
def get_last_update(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return f.read().strip()
    else:
        return "Nenhuma atualização realizada ainda."

def save_last_update(filename, timestamp):
    with open(filename, "w") as f:
        f.write(timestamp)


####BAIXANDO DADOS DO PRIORIZA---------------------------------------------------------------------------------------

def baixar_dados():
    st.write("Iniciando navegador...")
    navegador = webdriver.Edge()
    navegador.get("https://app.powerbi.com/groups/me/apps/7d1d1b76-89e3-44c6-8bac-36130117cfb9/reports/297edebe-ed1f-42e3-8d3d-5f313244ff81/ReportSection?ctid=5b6f6241-9a57-4be4-8e50-1dfa72e79a57&experience=power-bi")
    navegador.maximize_window()
    time.sleep(30)
    
    st.write("Clicando na barra de rolagem...")
    navegador.find_element(By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[15]/transform/div/div[3]/div/div/visual-modern/div/div/div[2]/div[4]').click()
    time.sleep(2)
    
    st.write("Clicando no ícone de exportação...")
    navegador.find_element(By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[15]/transform/div/visual-container-header/div/div/div/visual-container-options-menu/visual-header-item-container/div/button').click()
    time.sleep(2)
    
    st.write("Escolhendo exportação de dados...")
    navegador.find_element(By.XPATH, '//*[@id="6"]').click()
    time.sleep(2)
    
    navegador.find_element(By.XPATH, '//*[@id="pbi-radio-button-1"]/label/section').click()
    time.sleep(2)
    navegador.find_element(By.XPATH, '//*[@id="$pbi-dropdown-0"]/pbi-dropdown-trigger/p').click()
    time.sleep(2)
    navegador.find_element(By.XPATH, '/html/body/div[2]/div[6]/div/pbi-dropdown-overlay/div/div/pbi-dropdown-item[2]/div').click()
    time.sleep(2)
    navegador.find_element(By.XPATH, '/html/body/div[2]/div[4]/div/mat-dialog-container/div/div/export-data-dialog/mat-dialog-actions/button[1]').click()
    time.sleep(2)
    
    st.write("Salvando arquivo prioriza...")
    pyautogui.click(x=1792, y=71)
    time.sleep(3)
    pyautogui.click(x=1792, y=71)
    time.sleep(3)
    pyautogui.click(x=1511, y=198)
    time.sleep(3)
    
    pyautogui.typewrite('C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\prioriza.csv')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.press('left')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(10)
    
    st.success("Processo concluído!")
    # Registra a data/hora atual em arquivo
    ultima_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    save_last_update("last_update_prioriza.txt", ultima_atualizacao)
    st.write(f"Última atualização - Prioriza: {ultima_atualizacao}")

####--------------------------------------------------------------------------------------------------------------------

def baixar_pfceo():

    import pyautogui
    from selenium import webdriver

    st.write("Iniciando navegador...")
    navegador=webdriver.Edge()
    navegador.get("https://app.powerbi.com/reportEmbed?reportId=57f8941f-17d9-46f7-abb8-6cb5e277f7f9&appId=668573f4-2e20-475c-abac-42927def1dff&autoAuth=true&ctid=5b6f6241-9a57-4be4-8e50-1dfa72e79a57")
    navegador.maximize_window()

    import time
    time.sleep(20)

    #  element = driver.find_element(By.ID, "lname")
    from selenium.webdriver.common.by import By

    #filtrar RECAP
    navegador.find_element(By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[15]/transform/div/div[3]/div/div/visual-modern/div/div/div[2]/div/div[2]/div/div[2]/div').click()
    time.sleep(2)


    #clicar na barra de rolagem para aparecer icone de exportação
    navegador.find_element(By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[16]/transform/div/div[3]/div/div/div/div/div/div/h3').click()
    time.sleep(2)

    #clicar no icone de exportação
    navegador.find_element(By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[16]/transform/div/visual-container-header/div/div/div/visual-container-options-menu/visual-header-item-container/div/button').click()
    time.sleep(2)

    #escolher exportação de dados
    navegador.find_element(By.XPATH, '//*[@id="0"]').click()
    time.sleep(2)

    #escolher dados resumidos
    navegador.find_element(By.XPATH, '//*[@id="pbi-radio-button-1"]/label/section').click()
    time.sleep(2)


    #escolher botao csv
    navegador.find_element(By.XPATH, '//*[@id="$pbi-dropdown-0"]/pbi-dropdown-trigger/p').click()
    time.sleep(2)

    #escolher botao csv 30k
    pyautogui.click(x=744,y=901)
    time.sleep(2)

    #apertar botao verde
    pyautogui.click(x=1151,y=910)
    time.sleep(3)

    #apertar botao salvar planilha
    pyautogui.click(x= 1792,y=71)
    time.sleep(3)
    pyautogui.click(x=1792,y=71)
    time.sleep(3)
    pyautogui.click(x=1511, y=201)


    time.sleep(3)
    #notebook clicar em downloads 1792, 71
    #notebook clicar em salvar como 1551, 198
    #salvando nome do arquivo
    #pyautogui.doubleClick(x= 1125,y=474)
    #time.sleep(2)
    import pyautogui as caminho
    caminho.typewrite('C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\pfceo.csv')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.press('left')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(10) 
    st.success("Processo concluído!")
    # Registra a data/hora atual em arquivo
    ultima_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    save_last_update("last_update_prioriza.txt", ultima_atualizacao)
    st.write(f"Última atualização - Prioriza: {ultima_atualizacao}")

####--------------------------------------------------------------------------------------------------------------------



def baixar_IARI():
    import pyautogui
    from selenium import webdriver

    navegador=webdriver.Edge()
    navegador.get("https://app.powerbi.com/groups/me/apps/3a3ed9f7-5758-4f52-97b1-8c3c1d1071ab/reports/c5da251e-0ece-4c02-9093-7a19047a6dda/ReportSectiond516ea33d2adcc6654bb?experience=power-bi")
    navegador.maximize_window()

    import time
    time.sleep(20)

    #  element = driver.find_element(By.ID, "lname")
    from selenium.webdriver.common.by import By


    #clicar na barra de rolagem para aparecer icone de exportação
    navegador.find_element(By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[8]/transform/div/div[3]/div/div/div/div/div/div/h3').click()
    time.sleep(2)

    #clicar no icone de exportação
    navegador.find_element(By.XPATH, '//*[@id="pvExplorationHost"]/div/div/exploration/div/explore-canvas/div/div[2]/div/div[2]/div[2]/visual-container-repeat/visual-container[8]/transform/div/visual-container-header/div/div/div/visual-container-options-menu/visual-header-item-container/div/button').click()
    time.sleep(2)

    #escolher exportação de dados
    navegador.find_element(By.XPATH, '//*[@id="6"]').click()
    time.sleep(2)

    #escolher dados resumidos
    navegador.find_element(By.XPATH, '//*[@id="pbi-radio-button-1"]/label/section').click()
    time.sleep(2)


    #escolher botao csv
    navegador.find_element(By.XPATH, '//*[@id="$pbi-dropdown-0"]/pbi-dropdown-trigger/p').click()
    time.sleep(2)

    #escolher botao csv 30k
    pyautogui.click(x=744,y=901)
    time.sleep(2)

    #apertar botao verde
    pyautogui.click(x=1151,y=910)
    time.sleep(3)

    #apertar botao salvar planilha
    pyautogui.click(x= 1792,y=71)
    time.sleep(3)
    pyautogui.click(x=1792,y=71)
    time.sleep(3)
    pyautogui.click(x=1551,y=198)
    time.sleep(3)


    #notebook clicar em downloads 1792, 71
    #notebook clicar em salvar como 1551, 198
    #salvando nome do arquivo
    #pyautogui.doubleClick(x= 1125,y=474)
    #time.sleep(2)
    import pyautogui as caminho
    caminho.typewrite('C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\IARI.csv')
    time.sleep(2)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.press('left')

    time.sleep(2)
    pyautogui.press('enter')

    time.sleep(5)

    import pandas as pd
    #modificar IARI colunas
    df_iari = pd.read_csv('C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\IARI.csv')
    df_iari['Medida'] = df_iari['Medida'].apply(lambda x: str(x).split('-')[0])
    df_iari.rename(columns={'Medida': 'NOTA'}, inplace=True)
    df_iari.to_csv('C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\IARI.csv')



    time.sleep(10)





    st.success("Processo concluído!")
    # Registra a data/hora atual em arquivo
    ultima_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    save_last_update("last_update_prioriza.txt", ultima_atualizacao)
    st.write(f"Última atualização - Prioriza: {ultima_atualizacao}")

####--------------------------------------------------------------------------------------------------------------------



def abrir_e_atualizar():
    st.write("Atualizando database_indicadores...")
    caminho_excel = r'C:\Users\RSKG\OneDrive - PETROBRAS\C3\Banco de dados\database_indicadores.xlsx'
    wb = xw.Book(caminho_excel)
    # Atualiza todas as conexões da planilha
    wb.api.RefreshAll()
    time.sleep(30)
    wb.save()
    wb.close()
    st.success("Power BI aberto e banco de dados atualizado com sucesso!")
    # Registra a data/hora atual em arquivo
    ultima_atualizacao_db = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    save_last_update("last_update_database.txt", ultima_atualizacao_db)
    st.write(f"Última atualização - Database: {ultima_atualizacao_db}")

def abrir_e_atualizar_AR():
    st.write("Atualizar Planilha de AR")
    caminho_excel = r'C:\Users\RSKG\PETROBRAS\Solicitações de AR - General\Solicitações de AR.xlsm'
    wb = xw.Book(caminho_excel)
    # Atualiza todas as conexões da planilha
    wb.api.RefreshAll()
    time.sleep(10)
    wb.save()
    wb.close()
    st.success("Planilha de AR atualizada com sucesso!")
    # Registra a data/hora atual em arquivo
    ultima_atualizacao_ar = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    save_last_update("last_update_AR.txt", ultima_atualizacao_ar)
    st.write(f"Última atualização - AR: {ultima_atualizacao_ar}")


# Ao carregar a página, exibe os registros persistentes de última atualização
st.header("Registros de Atualizações")
ultima_prioriza = get_last_update("last_update_prioriza.txt")
st.write("Última atualização - Prioriza:", ultima_prioriza)
ultima_database = get_last_update("last_update_database.txt")
st.write("Última atualização - Database:", ultima_database)
ultima_ar = get_last_update("last_update_AR.txt")
st.write("Última atualização - AR:", ultima_ar)

# Seção de atualização de dados para Prioriza
st.subheader("Atualização de dados", divider="gray")
if st.button("Prioriza", key="prioriza"):
    baixar_dados()


# Seção de atualização de dados para pfceo
if st.button("PFCEO", key="pfceo"):
    baixar_pfceo()

# Seção de atualização de dados para IARI
if st.button("IARI", key="iari"):
    baixar_IARI()



# Seção de atualização para Database Indicadores
st.subheader("Atualizar Database Indicadores", divider="gray")
if st.button("Atualizar Database Indicadores", key="database_indicadores"):
    abrir_e_atualizar()

# Seção de atualização para Planilha de AR
st.subheader("Atualizar Planilha de AR", divider="gray")
if st.button("Atualizar Planilha de AR", key="planilha_ar"):
    abrir_e_atualizar_AR()

