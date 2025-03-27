import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO E ARQUIVOS ---
st.set_page_config(layout="wide", page_title="Planejamento das Ordens")

CSV_FILE = "ordens_status.csv"
CSV_PRIORIZA = "prioriza.csv"

if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Ordem", "Planejador", "Status", "Informações", "Última Atualização"]).to_csv(CSV_FILE, index=False)
if not os.path.exists(CSV_PRIORIZA):
    pd.DataFrame(columns=["ORDEM", "DESCRICAO", "GPM", "Status"]).to_csv(CSV_PRIORIZA, index=False)

# --- FUNÇÕES ---
def load_data():
    df = pd.read_csv(CSV_FILE)
    df.columns = df.columns.str.strip()
    return df

def save_data(df):
    try:
        df.to_csv(CSV_FILE, index=False)
    except Exception as e:
        st.error(f"Erro ao salvar o arquivo: {e}")

def load_prioriza():
    df = pd.read_csv(CSV_PRIORIZA)
    df.columns = df.columns.str.strip()
    if "ORDEM" in df.columns:
        df.rename(columns={"ORDEM": "Ordem"}, inplace=True)
    if "DESCRICAO" in df.columns and "Serviço_prioriza" not in df.columns:
        df.rename(columns={"DESCRICAO": "Serviço_prioriza"}, inplace=True)
    # Filtra apenas onde Status == "Microplanejamento"
    df = df[df["Status"] == "Microplanejamento"]
    return df

# --- ESTADO DA SESSÃO ---
if "last_ordem" not in st.session_state:
    st.session_state["last_ordem"] = ""
if "planejador_input" not in st.session_state:
    st.session_state["planejador_input"] = ""
if "status_input" not in st.session_state:
    st.session_state["status_input"] = []
if "info_input" not in st.session_state:
    st.session_state["info_input"] = ""
if "confirm_delete" not in st.session_state:
    st.session_state["confirm_delete"] = False

# --- SIDEBAR ---
st.sidebar.header("Atribuir Ordem")
ordem = st.sidebar.text_input("Número da Ordem", key="ordem_input")
status_options = ["Em planejamento", "AR", "Doc CQ", "IBTUG", "Materiais", "Definição MA", "SMS", "Outros", "Concluído"]

if ordem:
    df_status_temp = load_data()
    if ordem in df_status_temp["Ordem"].astype(str).values:
        st.sidebar.info("Esta ordem já existe. Ao salvar, os dados serão atualizados.")

def clear_fields():
    st.session_state["planejador_input"] = ""
    st.session_state["status_input"] = [status_options[0]]
    st.session_state["info_input"] = ""

if ordem:
    st.sidebar.button("Limpar dados", on_click=clear_fields, key="limpar_dados")
    
    df_status = load_data()
    planejador_val = ""
    status_val = ""
    info_val = ""
    if ordem in df_status["Ordem"].astype(str).values:
        idx = df_status[df_status["Ordem"].astype(str) == ordem].index[0]
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
    status_input = st.sidebar.multiselect("Status", options=status_options,
                                          default=st.session_state["status_input"],
                                          key="status_input")
    info_input = st.sidebar.text_area("Informações", value=st.session_state["info_input"], key="info_input")
    
    if st.sidebar.button("Salvar Atualização"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_str = ", ".join(status_input)
        df_status = load_data()
        if ordem in df_status["Ordem"].astype(str).values:
            idx = df_status[df_status["Ordem"].astype(str) == ordem].index[0]
            df_status.at[idx, "Planejador"] = planejador_input
            df_status.at[idx, "Status"] = status_str
            df_status.at[idx, "Informações"] = info_input
            df_status.at[idx, "Última Atualização"] = now
            st.sidebar.success("Ordem atualizada com sucesso!")
        else:
            new_row = pd.DataFrame({
                "Ordem": [ordem],
                "Planejador": [planejador_input],
                "Status": [status_str],
                "Informações": [info_input],
                "Última Atualização": [now]
            })
            df_status = pd.concat([df_status, new_row], ignore_index=True)
            st.sidebar.success("Nova ordem inserida com sucesso!")
        save_data(df_status)
        if hasattr(st, 'experimental_rerun'):
            st.experimental_rerun()
    
    # Botão para apagar a ordem com confirmação
    if st.sidebar.button("Apagar Ordem") and not st.session_state["confirm_delete"]:
        st.session_state["confirm_delete"] = True

    if st.session_state["confirm_delete"]:
        st.sidebar.write("Tem certeza que deseja apagar a ordem?")
        col1, col2 = st.sidebar.columns(2)
        if col1.button("Sim", key="delete_yes"):
            df_status = load_data()
            if ordem in df_status["Ordem"].astype(str).values:
                df_status = df_status[df_status["Ordem"].astype(str) != ordem]
                save_data(df_status)
                st.sidebar.success("Ordem apagada de ordens_status!")
            else:
                st.sidebar.error("Ordem não encontrada em ordens_status!")
            st.session_state["confirm_delete"] = False
            if hasattr(st, 'experimental_rerun'):
                st.experimental_rerun()
        if col2.button("Não", key="delete_no"):
            st.sidebar.info("Exclusão cancelada.")
            st.session_state["confirm_delete"] = False

# --- ÁREA PRINCIPAL ---
st.header("Planejamento de Ordens")

st.subheader("Filtro de GPM (visualização)")
df_prioriza_for_filter = load_prioriza()
gpm_values = df_prioriza_for_filter["GPM"].dropna().unique().tolist()
selected_gpm = st.multiselect("Selecione GPM", options=gpm_values, key="gpm_filter_main")

# Carrega dados para visualização
df_status = load_data()
df_status = df_status.rename(columns={"Status": "Status_status"})
df_prioriza = load_prioriza()

df_merged = pd.merge(df_status, df_prioriza, on="Ordem", how="outer")

# Garante a existência das colunas desejadas
for col in ["Serviço_prioriza"]:
    if col not in df_merged.columns:
        df_merged[col] = ""

colunas_desejadas = ["Ordem", "Serviço_prioriza", "GPM", "Planejador", "Status_status", "Informações", "Última Atualização"]
df_final = df_merged[colunas_desejadas]

df_final = df_final.rename(columns={
    "Status_status": "Serviço_status",
    "Última Atualização": "ultima atualização",
    "Informações": "informações"
})

if selected_gpm:
    df_final = df_final[df_final["GPM"].isin(selected_gpm)]
    
st.dataframe(df_final, use_container_width=True, height=600)
