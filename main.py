import ssl
# Desabilita a verificação de certificados SSL (somente para desenvolvimento/teste)
ssl._create_default_https_context = ssl._create_unverified_context

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from supabase import create_client, Client

# --- CONFIGURAÇÃO DO SUPABASE ---
supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
supabase_key = st.secrets["supabase"]["SUPABASE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)

# --- FUNÇÕES PARA A TABELA "ordens_status" NO SUPABASE ---
def load_data_supabase():
    response = supabase.table("ordens_status").select("*").execute()
    data = response.data if response.data is not None else []
    df = pd.DataFrame(data)
    if not df.empty:
        df.columns = df.columns.str.strip()
    return df

def save_data_supabase(record):
    # Upsert: insere ou atualiza com base na coluna "Ordem"
    response = supabase.table("ordens_status").upsert(record, on_conflict="Ordem").execute()
    return response

def delete_data_supabase(ordem):
    response = supabase.table("ordens_status").delete().eq("Ordem", ordem).execute()
    return response

# --- FUNÇÃO PARA CARREGAR O ARQUIVO LOCAL "prioriza.csv" (REFERÊNCIA) ---
def load_prioriza_local():
    if os.path.exists("prioriza.csv"):
        df = pd.read_csv("prioriza.csv", dtype=str)
    else:
        df = pd.DataFrame(columns=["ORDEM", "DESCRICAO", "GPM", "Status"])
    df.columns = df.columns.str.strip()
    if "ORDEM" in df.columns:
        df.rename(columns={"ORDEM": "Ordem"}, inplace=True)
    if "DESCRICAO" in df.columns and "Serviço_prioriza" not in df.columns:
        df.rename(columns={"DESCRICAO": "Serviço_prioriza"}, inplace=True)
    # Filtra apenas as linhas com os Status de interesse
    df = df[df["Status"].isin(["Microplanejamento", "Falta material", "TO GPI - Aguarda TRIA", "Programável", "TM GPI - Aguarda MAN"])]
    return df

# --- ESTADO DA SESSÃO ---
if "ordem_input" not in st.session_state:
    st.session_state["ordem_input"] = ""
if "last_ordem" not in st.session_state:
    st.session_state["last_ordem"] = ""
if "planejador_input" not in st.session_state:
    st.session_state["planejador_input"] = ""
if "status_input" not in st.session_state or not st.session_state["status_input"]:
    st.session_state["status_input"] = []
if "info_input" not in st.session_state:
    st.session_state["info_input"] = ""
if "confirm_delete" not in st.session_state:
    st.session_state["confirm_delete"] = False

# --- SIDEBAR: CADASTRO/ATUALIZAÇÃO ---
st.sidebar.header("Atribuir Ordem")
ordem = st.sidebar.text_input("Número da Ordem", key="ordem_input")
status_options = ["Em planejamento", "AR", "Doc CQ", "IBTUG", "Materiais", "Definição MA", "SMS", "Outros", "Proposta Pacotes", "Concluído"]

if ordem:
    df_status_temp = load_data_supabase()
    if ordem.strip() in df_status_temp["Ordem"].astype(str).str.strip().values:
        st.sidebar.info("Esta ordem já existe. Ao salvar, os dados serão atualizados.")

def clear_fields():
    st.session_state["ordem_input"] = ""
    st.session_state["planejador_input"] = ""
    st.session_state["status_input"] = [status_options[0]]
    st.session_state["info_input"] = ""
    st.session_state["last_ordem"] = ""
    st.experimental_rerun()

if ordem:
    st.sidebar.button("Limpar dados", on_click=clear_fields, key="limpar_dados")
    
    df_status = load_data_supabase()
    planejador_val = ""
    status_val = ""
    info_val = ""
    if ordem.strip() in df_status["Ordem"].astype(str).str.strip().values:
        idx = df_status[df_status["Ordem"].astype(str).str.strip() == ordem.strip()].index[0]
        planejador_val = df_status.at[idx, "Planejador"]
        status_val = df_status.at[idx, "Status"]
        info_val = df_status.at[idx, "Informações"]
    if pd.isna(planejador_val): planejador_val = ""
    if pd.isna(status_val) or status_val == "": status_val = ""
    if pd.isna(info_val): info_val = ""
    
    if st.session_state.get("last_ordem") != ordem:
        st.session_state["planejador_input"] = planejador_val
        st.session_state["status_input"] = [s.strip() for s in status_val.split(",")] if status_val else [status_options[0]]
        st.session_state["info_input"] = info_val
        st.session_state["last_ordem"] = ordem
    
    planejador_input = st.sidebar.text_input("Planejador", value=st.session_state["planejador_input"], key="planejador_input")
    status_input = st.sidebar.multiselect("Status", options=status_options, key="status_input")
    info_input = st.sidebar.text_area("Informações", value=st.session_state["info_input"], key="info_input")
    
    if st.sidebar.button("Salvar Atualização"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_str = ", ".join(status_input)
        record = {
            "Ordem": ordem.strip(),
            "Planejador": planejador_input,
            "Status": status_str,
            "Informações": info_input,
            "Última Atualização": now
        }
        save_data_supabase(record)
        st.sidebar.success("Ordem salva com sucesso!")
        st.experimental_rerun()
    
    if st.sidebar.button("Apagar Ordem") and not st.session_state["confirm_delete"]:
        st.session_state["confirm_delete"] = True
    if st.session_state["confirm_delete"]:
        st.sidebar.write("Tem certeza que deseja apagar a ordem?")
        col1, col2 = st.sidebar.columns(2)
        if col1.button("Sim", key="delete_yes"):
            delete_data_supabase(ordem.strip())
            st.sidebar.success("Ordem apagada com sucesso!")
            st.session_state["confirm_delete"] = False
            st.experimental_rerun()
        if col2.button("Não", key="delete_no"):
            st.sidebar.info("Exclusão cancelada.")
            st.session_state["confirm_delete"] = False

# --- ÁREA PRINCIPAL: VISUALIZAÇÃO ---
st.header("Planejamento de Ordens")
st.subheader("Filtro de GPM (visualização)")
df_prioriza_for_filter = load_prioriza_local()
gpm_values = df_prioriza_for_filter["GPM"].dropna().unique().tolist()
selected_gpm = st.multiselect("Selecione GPM", options=gpm_values, key="gpm_filter_main")

filtro_ordem = ordem.strip() if ordem else None

df_status = load_data_supabase()
df_status = df_status.rename(columns={"Status": "Status_status"})
df_prioriza = load_prioriza_local()

df_merged = pd.merge(df_status, df_prioriza, on="Ordem", how="outer")
if "Serviço_prioriza" not in df_merged.columns:
    df_merged["Serviço_prioriza"] = ""

colunas_desejadas = ["Ordem", "Serviço_prioriza", "GPM", "Planejador", "Status_status", "Informações", "Última Atualização"]
df_final = df_merged[colunas_desejadas]

df_final = df_final.rename(columns={
    "Status_status": "Serviço_status",
    "Última Atualização": "ultima atualização",
    "Informações": "informações"
})

if selected_gpm:
    df_final = df_final[df_final["GPM"].isin(selected_gpm)]
    
if filtro_ordem:
    df_final = df_final[df_final["Ordem"].astype(str).str.strip() == filtro_ordem]
    
st.dataframe(df_final, use_container_width=True, height=600)
