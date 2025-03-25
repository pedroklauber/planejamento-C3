import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da página em modo wide
st.set_page_config(layout="wide", page_title="Planejamento das Ordens")

# Defina o caminho do CSV
CSV_FILE = "ordens_status.csv"

# Se o arquivo CSV não existir, crie-o com as colunas necessárias
if not os.path.exists(CSV_FILE):
    df_temp = pd.DataFrame(columns=["Ordem", "Serviço", "Planejador", "Status", "Informações", "Última Atualização"])
    df_temp.to_csv(CSV_FILE, index=False)

def load_data():
    return pd.read_csv(CSV_FILE)

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# Inicializa a variável de controle para confirmação de exclusão
if "confirm_delete" not in st.session_state:
    st.session_state["confirm_delete"] = False

def update_sidebar():
    st.sidebar.header("Atribuir Ordem")
    ordem = st.sidebar.text_input("Número da Ordem", key="ordem_input")
    
    status_options = ["Em planejamento", "AR","Doc CQ", "IBTUG","Materiais","Definição MA","SMS", "Outros","Concluído"]
    
    if ordem:
        # Botão para limpar os dados dos campos abaixo de "Número da Ordem"
        if st.sidebar.button("Limpar dados", key="limpar_dados"):
         
            st.session_state["servico_input"] = ""
            st.session_state["planejador_input"] = ""
            st.session_state["info_input"] = ""
            st.session_state["status_input"] = [status_options[0]]
        
        df = load_data()
        if ordem in df["Ordem"].astype(str).values:
            index = df[df["Ordem"].astype(str) == ordem].index[0]
            servico_atual = df.at[index, "Serviço"]
            planejador_atual = df.at[index, "Planejador"]
            status_atual = df.at[index, "Status"] if "Status" in df.columns else ""
            info_atual = df.at[index, "Informações"] if "Informações" in df.columns else ""

            # Converte o status salvo (string) em lista para o multiselect

            if status_atual:
                default_status = [s.strip() for s in status_atual.split(",")]
            else:
                default_status = [status_options[0]]
        else:
            servico_atual = ""
            planejador_atual = ""
            default_status = [status_options[0]]
            info_atual = ""
        
        # Os valores dos inputs serão priorizados conforme o st.session_state (se definido)
        servico_manual = st.sidebar.text_input("Serviço", value=servico_atual, key="servico_input")
        planejador_manual = st.sidebar.text_input("Planejador", value=planejador_atual, key="planejador_input")
        info_manual = st.sidebar.text_area("Informações", value=info_atual, key="info_input")
        
        # Alterado para multiselect, permitindo várias seleções
        status_manual = st.sidebar.multiselect("Status", options=status_options, default=default_status, key="status_input")
        
        if st.sidebar.button("Salvar Atualização"):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Converter a lista de status em string, separando por vírgula
            status_str = ", ".join(status_manual)
            if ordem in df["Ordem"].astype(str).values:
                index = df[df["Ordem"].astype(str) == ordem].index[0]
                df.at[index, "Serviço"] = servico_manual
                df.at[index, "Planejador"] = planejador_manual
                df.at[index, "Status"] = status_str
                df.at[index, "Informações"] = info_manual
                df.at[index, "Última Atualização"] = now
            else:
                new_row = pd.DataFrame({
                    "Ordem": [ordem],
                    "Serviço": [servico_manual],
                    "Planejador": [planejador_manual],
                    "Status": [status_str],
                    "Informações": [info_manual],
                    "Última Atualização": [now]
                })
                df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.sidebar.success("Ordem atualizada com sucesso!")
        
        # Botão para iniciar a exclusão
        if st.sidebar.button("Apagar Ordem"):
            st.session_state.confirm_delete = True
        
        # Se a confirmação estiver ativa, exibe a pergunta com botões "Sim" e "Não"
        if st.session_state.confirm_delete:
            st.sidebar.write("Tem certeza que deseja excluir?")
            col1, col2 = st.sidebar.columns(2)
            if col1.button("Sim", key="delete_yes"):
                df = load_data()
                if ordem in df["Ordem"].astype(str).values:
                    df = df[df["Ordem"].astype(str) != ordem]
                    save_data(df)
                    st.sidebar.success("Ordem apagada com sucesso!")
                else:
                    st.sidebar.error("Ordem não encontrada para apagar!")
                st.session_state.confirm_delete = False
            if col2.button("Não", key="delete_no"):
                st.sidebar.info("Exclusão cancelada")
                st.session_state.confirm_delete = False

# Exibe a funcionalidade de atualização na sidebar
update_sidebar()

# Corpo principal: exibição do Banco de Dados de Ordens
st.header("Planejamento de Ordens")

df_display = load_data()

# Define a ordem desejada das colunas para exibição
col_order = ["Ordem", "Serviço", "Planejador", "Status", "Informações", "Última Atualização"]
df_display = df_display[[col for col in col_order if col in df_display.columns]]
st.dataframe(df_display, use_container_width=True)
