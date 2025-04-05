import streamlit as st
import pandas as pd
import os
from datetime import datetime
import ssl
from supabase import create_client, Client
import httpx




# --- CONFIGURAÇÃO E ARQUIVOS ---
st.set_page_config(layout="wide", page_title="Planejamento das Ordens")
chave = "RSKG"
CSV_FILE = f"C:\\Users\\{chave}\\PETROBRAS\\Serviços Integrados de Rotina - Documentos\\Rotina RECAP\\ordens_status.csv"
#CSV_FILE = f"https://petrobrasbr.sharepoint.com/ServiosIntegradosdeRotina/EfE_oPXa9gFFiLKl3pOeQzUBqACOB9qIpfpUKBrEm9gCrw?e=tl2Qib"

#https://petrobrasbr.sharepoint.com/ServiosIntegradosdeRotina/EfE_oPXa9gFFiLKl3pOeQzUBqACOB9qIpfpUKBrEm9gCrw?e=tl2Qib


# Cria o arquivo com as colunas necessárias, se não existir
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Ordem", "Planejador", "Status", "Informações", "Última Atualização", "Serviço_prioriza", "GPM"]).to_csv(CSV_FILE, index=False)

# --- FUNÇÕES DE LEITURA E SALVAMENTO ---
def load_data():
    df = pd.read_csv(CSV_FILE, dtype=str)
    df.columns = df.columns.str.strip()
    # Garante que as novas colunas existam
    for col in ["Serviço_prioriza", "GPM"]:
        if col not in df.columns:
            df[col] = ""
    return df

def save_data(df):
    try:
        df.to_csv(CSV_FILE, index=False)
    except Exception as e:
        st.error(f"Erro ao salvar o arquivo: {e}")

# --- ESTADO DA SESSÃO ---
if "ordem_input" not in st.session_state:
    st.session_state["ordem_input"] = ""
if "last_ordem" not in st.session_state:
    st.session_state["last_ordem"] = ""
if "planejador_input" not in st.session_state:
    st.session_state["planejador_input"] = ""
if "status_input" not in st.session_state or not st.session_state["status_input"]:
    st.session_state["status_input"] = ["Em planejamento"]
if "info_input" not in st.session_state:
    st.session_state["info_input"] = ""
if "servico_prioriza_input" not in st.session_state:
    st.session_state["servico_prioriza_input"] = ""
if "gpm_input" not in st.session_state:
    st.session_state["gpm_input"] = ""
if "confirm_delete" not in st.session_state:
    st.session_state["confirm_delete"] = False

# --- SIDEBAR: Cadastro/Atualização ---
st.sidebar.header("Atribuir Ordem")
ordem = st.sidebar.text_input("Número da Ordem", key="ordem_input")
status_options = ["Em planejamento", "AR", "Doc CQ", "IBTUG", "Materiais", "Definição MA", "SMS", "Outros", "Proposta Pacotes", "Concluído"]

if ordem:
    df_status_temp = load_data()
    if ordem.strip() in df_status_temp["Ordem"].astype(str).str.strip().values:
        st.sidebar.info("Esta ordem já existe. Ao salvar, os dados serão atualizados.")

def clear_fields():
    st.session_state["ordem_input"] = ""
    st.session_state["planejador_input"] = ""
    st.session_state["status_input"] = [status_options[0]]
    st.session_state["info_input"] = ""
    st.session_state["servico_prioriza_input"] = ""
    st.session_state["gpm_input"] = ""
    st.session_state["last_ordem"] = ""
    if hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()

if ordem:
    st.sidebar.button("Limpar dados", on_click=clear_fields, key="limpar_dados")
    
    df_status = load_data()
    planejador_val = ""
    status_val = ""
    info_val = ""
    servico_prioriza_val = ""
    gpm_val = ""
    if ordem.strip() in df_status["Ordem"].astype(str).str.strip().values:
        idx = df_status[df_status["Ordem"].astype(str).str.strip() == ordem.strip()].index[0]
        planejador_val = df_status.at[idx, "Planejador"]
        status_val = df_status.at[idx, "Status"]
        info_val = df_status.at[idx, "Informações"]
        servico_prioriza_val = df_status.at[idx, "Serviço_prioriza"]
        gpm_val = df_status.at[idx, "GPM"]
    if pd.isna(planejador_val): planejador_val = ""
    if pd.isna(status_val) or status_val == "": status_val = ""
    if pd.isna(info_val): info_val = ""
    if pd.isna(servico_prioriza_val): servico_prioriza_val = ""
    if pd.isna(gpm_val): gpm_val = ""
    
    if st.session_state.get("last_ordem") != ordem:
        st.session_state["planejador_input"] = planejador_val
        st.session_state["status_input"] = [s.strip() for s in status_val.split(",")] if status_val else [status_options[0]]
        st.session_state["info_input"] = info_val
        st.session_state["servico_prioriza_input"] = servico_prioriza_val
        st.session_state["gpm_input"] = gpm_val
        st.session_state["last_ordem"] = ordem
    
    planejador_input = st.sidebar.text_input("Planejador", value=st.session_state["planejador_input"], key="planejador_input")
    status_input = st.sidebar.multiselect("Status", options=status_options, key="status_input")
    info_input = st.sidebar.text_area("Informações", value=st.session_state["info_input"], key="info_input")
    servico_prioriza_input = st.sidebar.text_input("Serviço Prioriza", value=st.session_state["servico_prioriza_input"], key="servico_prioriza_input")
    gpm_input = st.sidebar.text_input("GPM", value=st.session_state["gpm_input"], key="gpm_input")
    
    if st.sidebar.button("Salvar Atualização"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_str = ", ".join(status_input)
        df_status = load_data()
        if ordem.strip() in df_status["Ordem"].astype(str).str.strip().values:
            idx = df_status[df_status["Ordem"].astype(str).str.strip() == ordem.strip()].index[0]
            df_status.at[idx, "Planejador"] = planejador_input
            df_status.at[idx, "Status"] = status_str
            df_status.at[idx, "Informações"] = info_input
            df_status.at[idx, "Serviço_prioriza"] = servico_prioriza_input
            df_status.at[idx, "GPM"] = gpm_input
            df_status.at[idx, "Última Atualização"] = now
            st.sidebar.success("Ordem atualizada com sucesso!")
        else:
            new_row = pd.DataFrame({
                "Ordem": [ordem.strip()],
                "Planejador": [planejador_input],
                "Status": [status_str],
                "Informações": [info_input],
                "Serviço_prioriza": [servico_prioriza_input],
                "GPM": [gpm_input],
                "Última Atualização": [now]
            })
            df_status = pd.concat([df_status, new_row], ignore_index=True)
            st.sidebar.success("Nova ordem inserida com sucesso!")
        save_data(df_status)
        if hasattr(st, 'experimental_rerun'):
            st.experimental_rerun()
    
    if st.sidebar.button("Apagar Ordem") and not st.session_state["confirm_delete"]:
        st.session_state["confirm_delete"] = True

    if st.session_state["confirm_delete"]:
        st.sidebar.write("Tem certeza que deseja apagar a ordem?")
        col1, col2 = st.sidebar.columns(2)
        if col1.button("Sim", key="delete_yes"):
            df_status = load_data()
            if ordem.strip() in df_status["Ordem"].astype(str).str.strip().values:
                df_status = df_status[df_status["Ordem"].astype(str).str.strip() != ordem.strip()]
                save_data(df_status)
                st.sidebar.success("Ordem apagada!")
            else:
                st.sidebar.error("Ordem não encontrada!")
            st.session_state["confirm_delete"] = False
            if hasattr(st, 'experimental_rerun'):
                st.experimental_rerun()
        if col2.button("Não", key="delete_no"):
            st.sidebar.info("Exclusão cancelada.")
            st.session_state["confirm_delete"] = False

# --- ÁREA PRINCIPAL: Visualização ---
st.header("Planejamento de Ordens")
st.subheader("Filtro de GPM (visualização)")
df_status = load_data()
gpm_values = df_status["GPM"].dropna().unique().tolist()
selected_gpm = st.multiselect("Selecione GPM", options=gpm_values, key="gpm_filter_main")

df_final = df_status.copy()
colunas_desejadas = ["Ordem", "Serviço_prioriza", "GPM", "Planejador", "Status", "Informações", "Última Atualização"]
df_final = df_final[colunas_desejadas]
df_final = df_final.rename(columns={
    "Status": "Serviço_status",
    "Última Atualização": "ultima atualização",
    "Informações": "informações"
})

if selected_gpm:
    df_final = df_final[df_final["GPM"].isin(selected_gpm)]
    
if ordem:
    df_final = df_final[df_final["Ordem"].astype(str).str.strip() == ordem.strip()]
    
st.dataframe(df_final, use_container_width=True, height=600)
