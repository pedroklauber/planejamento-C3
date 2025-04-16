# sidebar_db_update.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Caminho para o CSV
CSV_FILE = "C:\\Users\\RSKG\\OneDrive - PETROBRAS\\C3\\Banco de dados\\ordens_status.csv"

# Se o CSV não existir, cria com a coluna "Categoria"
if not os.path.exists(CSV_FILE):
    df_temp = pd.DataFrame(columns=["Ordem", "Informações", "Serviço", "Última Atualização", "Categoria"])
    df_temp.to_csv(CSV_FILE, index=False)

def load_data():
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

def update_sidebar():
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
            df = load_data()  # Recarrega os dados para garantir a atualização
            if ordem in df["Ordem"].astype(str).values:
                df = df[df["Ordem"].astype(str) != ordem]
                save_data(df)
                st.sidebar.success("Ordem apagada com sucesso!")
            else:
                st.sidebar.error("Ordem não encontrada para apagar!")

