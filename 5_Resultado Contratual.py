import streamlit as st
import time
import pandas as pd
import pyautogui as pag
import xlwings as xw
from selenium import webdriver
from selenium.webdriver.common.by import By
from plyer import notification
from datetime import datetime

# Configuração para tela larga
st.set_page_config(layout="wide")

def abrir_e_atualizar():
    # Abre o Power BI com Selenium
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
    
    pag.click(x=1511, y=198)
    time.sleep(3)
    pag.typewrite('C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\apontamentos.csv')
    time.sleep(2)
    pag.press('enter')
    time.sleep(2)
    pag.press('left')
    time.sleep(2)
    pag.press('enter')
    time.sleep(10)
    
    st.write("Atualizando planilha...")
    caminho_excel = r'C:\Users\RSKG\OneDrive - PETROBRAS\C3\Banco de dados\Acompanhamento Cumprimento da Programacao.xlsm'
    
    # Abre o Excel criando uma nova instância (para evitar conflitos)
    app = xw.App(visible=True)
    wb = app.books.open(caminho_excel)
    
    time.sleep(5)
    
    atualizado = False
    # Percorre as conexões da planilha procurando a "2.Apontamentos"
    for connection in wb.api.Connections:
        if connection.Name.strip() == "2.Apontamentos":
            st.write(f"Conexão encontrada: {connection.Name}")
            try:
                if hasattr(connection, 'OLEDBConnection'):
                    st.write("Atualizando via OLEDBConnection...")
                    connection.OLEDBConnection.BackgroundQuery = False
                    connection.OLEDBConnection.Refresh()
                    atualizado = True
                elif hasattr(connection, 'ODBCConnection'):
                    st.write("Atualizando via ODBCConnection...")
                    connection.ODBCConnection.BackgroundQuery = False
                    connection.ODBCConnection.Refresh()
                    atualizado = True
                else:
                    st.write("Atualizando via método Refresh()...")
                    connection.Refresh()
                    atualizado = True
            except Exception as e:
                st.write("Erro ao atualizar a conexão '2.Apontamentos':", e)
    
    if not atualizado:
        st.write("Não foi possível atualizar a conexão específica. Tentando atualizar todas as conexões com RefreshAll()...")
        try:
            wb.api.RefreshAll()
            atualizado = True
        except Exception as e:
            st.write("Erro ao atualizar todas as conexões:", e)
    
    time.sleep(10)  # Aguarda a conclusão da atualização
    wb.save()
    wb.close()
    app.quit()
    st.success("Power BI aberto e banco de dados atualizado com sucesso!")

def processar_dados():
    st.write("Processando dados...")
    caminho_excel = r'C:\Users\RSKG\OneDrive - PETROBRAS\C3\Banco de dados\Acompanhamento Cumprimento da Programacao.xlsm'
    xls = pd.ExcelFile(caminho_excel)
    df = pd.read_excel(xls, sheet_name="4. Resultado Contratual")
    df.rename(columns={
        "GPM": "GERENCIA",
        "RS PETROBRAS GERENCIA": "RS por GERENCIA",
        " Cumprimento\nAgregado": "Cumprimento Agregado",
        "Meta por dia": "META DIARIA",
        "Centro Trabalho": "CENTRO_TRABALHO",
        "SUPERVISÃO": "SUPERVISAO"
    }, inplace=True)
    df = df.loc[:, ~df.columns.duplicated()]
    
    df["RS por GERENCIA"] = (pd.to_numeric(df["RS por GERENCIA"], errors="coerce") * 100).round(2)
    df["RS por Centro"] = (pd.to_numeric(df["RS por Centro"], errors="coerce") * 100).round(2)
    df["Cumprimento Agregado"] = (pd.to_numeric(df["Cumprimento Agregado"], errors="coerce") * 100).round(2)
    df["META DIARIA"] = (pd.to_numeric(df["META DIARIA"], errors="coerce") * 100).round(2)
    df["OM Fator Ocupação"] = (pd.to_numeric(df["OM Fator Ocupação"], errors="coerce") * 100).round(2)
    
    df = df[['GERENCIA', 'RS por GERENCIA', 'Cumprimento Agregado', 'META DIARIA', 'SUPERVISAO', 'CENTRO_TRABALHO', 'RS por Centro', 'OM Fator Ocupação']]
    resumo = "📊 **Relatório de Acompanhamento**\n\n"
    gerencias_abaixo_meta = df[df["RS por GERENCIA"] < df["META DIARIA"]]
    resumo += "⚠️ **Gerências abaixo da meta (Contratual):**\n"
    for _, row in gerencias_abaixo_meta.iterrows():
        diferenca = row["META DIARIA"] - row["RS por GERENCIA"]
        resumo += f"- {row['GERENCIA']}: {row['RS por GERENCIA']:.2f}% (abaixo por {diferenca:.2f}%) | Meta: {row['META DIARIA']:.2f}%\n"
    
    resumo += "\n📌 **Percentuais Realização Contratual:**\n"
    for _, row in df.iterrows():
        resumo += f"- {row['CENTRO_TRABALHO']}: {row['RS por Centro']:.2f}% | Meta: {row['META DIARIA']:.2f}%\n"
    
    resumo += "\n📌 **Cumprimento por Supervisão e Centro de Trabalho:**\n"
    df_supervisao = df.groupby(["SUPERVISAO", "CENTRO_TRABALHO"], as_index=False)["Cumprimento Agregado"].mean()
    for _, row in df_supervisao.iterrows():
        resumo += f"- {row['SUPERVISAO']} | {row['CENTRO_TRABALHO']}: {row['Cumprimento Agregado']:.2f}%\n"
    
    st.markdown(resumo)
    return df, resumo

def processar_falta_quebra():
    st.write("Filtrando registros com 'Falta quebra'...")
    caminho_excel = r'C:\Users\RSKG\OneDrive - PETROBRAS\C3\Banco de dados\Acompanhamento Cumprimento da Programacao.xlsm'
    xls = pd.ExcelFile(caminho_excel)
    df_apontamentos = pd.read_excel(xls, sheet_name="2.Apontamentos")
    
    df_apontamentos_filtro = df_apontamentos[df_apontamentos["Quebra pend"] == "Falta quebra"]
    
    colunas_desejadas = ["GPM", "CT", "Ordem", "Operação", "Texto operação", "Nome", "Quebra"]
    df_apontamentos_filtro = df_apontamentos_filtro[colunas_desejadas]

    st.subheader("Registros Imediatas com 'Falta quebra'")
    st.dataframe(df_apontamentos_filtro)

    return df_apontamentos_filtro

def main():
    st.title("RESULTADO REALIZAÇÃO SEMANAL")
    st.write("Abrindo Power BI e atualizando banco de dados...")
    st.write("Última atualização:", datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    
    if st.button("Abrir Power BI e Atualizar Banco de Dados"):
        abrir_e_atualizar()
        notification.notify(title="Banco de Dados Concluída", 
                            message="✅ Apontamentos atualizados.", 
                            timeout=10)
    
    if st.button("Processar Dados"):
        df, resumo = processar_dados()
        st.write("Dados processados com sucesso!")
        
        tabela1 = df[['CENTRO_TRABALHO', 'SUPERVISAO', 'RS por Centro', 'Cumprimento Agregado', 'OM Fator Ocupação']]
        tabela2 = df[['GERENCIA', 'RS por GERENCIA', 'META DIARIA']].dropna()
        tabela2 = tabela2[(tabela2['GERENCIA'] != '') & (tabela2['RS por GERENCIA'] != '')]
        
        st.subheader("Realização Semanal por Centro de Trabalho")
        st.dataframe(tabela1, 
                     column_config={"RS por Centro": st.column_config.ProgressColumn("RS por Centro", help="", format="", min_value=0, max_value=100)},
                     hide_index=True)
        
        st.subheader("Realização Semanal por Centro de Trabalho por Gerencia")
        st.dataframe(tabela2)
      
        processar_falta_quebra()
        st.write("Dados processados com sucesso!")

        notification.notify(title="Atualização Concluída", 
                            message="✅ Apontamentos atualizados.", 
                            timeout=10)

if __name__ == "__main__":
    main()
