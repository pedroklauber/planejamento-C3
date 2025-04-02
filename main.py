import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO E ARQUIVOS ---
st.set_page_config(layout="wide", page_title="Planejamento das Ordens")
chave = "RSKG"
CSV_FILE = f"C:\\Users\\{chave}\\PETROBRAS\\Serviços Integrados de Rotina - Documentos\\Rotina RECAP\\ordens_status.csv"

# Cria o arquivo com as colunas necessárias, se não existir
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Ordem", "Serviço_prioriza", "GPM", "Planejador", "Status", "Informações", "Última Atualização"]).to_csv(CSV_FILE, index=False)

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
if "servico_input" not in st.session_state:
    st.session_state["servico_input"] = ""
if "gpm_input" not in st.session_state:
    st.session_state["gpm_input"] = "CAL"
if "planejador_input" not in st.session_state:
    st.session_state["planejador_input"] = ""
if "status_input" not in st.session_state or not st.session_state["status_input"]:
    st.session_state["status_input"] = ["Em planejamento"]
if "info_input" not in st.session_state:
    st.session_state["info_input"] = ""
if "confirm_delete" not in st.session_state:
    st.session_state["confirm_delete"] = False

# --- SIDEBAR: Cadastro/Atualização ---
st.sidebar.header("Atribuir Ordem")
# Ordem
ordem = st.sidebar.text_input("Número da Ordem", key="ordem_input")

# Se a ordem já existir, informar o usuário
if ordem:
    df_status_temp = load_data()
    if ordem.strip() in df_status_temp["Ordem"].astype(str).str.strip().values:
        st.sidebar.info("Esta ordem já existe. Ao salvar, os dados serão atualizados.")

# Função para limpar os campos
def clear_fields():
    st.session_state["ordem_input"] = ""
    st.session_state["servico_input"] = ""
    st.session_state["gpm_input"] = "CAL"
    st.session_state["planejador_input"] = ""
    st.session_state["status_input"] = ["Em planejamento"]
    st.session_state["info_input"] = ""
    st.session_state["last_ordem"] = ""
    if hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()

if ordem:
    st.sidebar.button("Limpar dados", on_click=clear_fields, key="limpar_dados")
    
    df_status = load_data()
    servico_val = ""
    gpm_val = ""
    planejador_val = ""
    status_val = ""
    info_val = ""
    if ordem.strip() in df_status["Ordem"].astype(str).str.strip().values:
        idx = df_status[df_status["Ordem"].astype(str).str.strip() == ordem.strip()].index[0]
        servico_val = df_status.at[idx, "Serviço_prioriza"]
        gpm_val = df_status.at[idx, "GPM"]
        planejador_val = df_status.at[idx, "Planejador"]
        status_val = df_status.at[idx, "Status"]
        info_val = df_status.at[idx, "Informações"]
    if pd.isna(servico_val): servico_val = ""
    if pd.isna(gpm_val): gpm_val = ""
    if pd.isna(planejador_val): planejador_val = ""
    if pd.isna(status_val) or status_val == "": status_val = ""
    if pd.isna(info_val): info_val = ""
    
    # Atualiza os valores na sessão se a ordem mudou
    if st.session_state.get("last_ordem") != ordem:
        st.session_state["servico_input"] = servico_val
        st.session_state["gpm_input"] = gpm_val if gpm_val else "CAL"
        st.session_state["planejador_input"] = planejador_val
        st.session_state["status_input"] = [s.strip() for s in status_val.split(",")] if status_val else ["Em planejamento"]
        st.session_state["info_input"] = info_val
        st.session_state["last_ordem"] = ordem
    
    # Campos do formulário na ordem solicitada
    servico_input = st.sidebar.text_input("Serviço", value=st.session_state["servico_input"], key="servico_input")
    gpm_options = ["CAL", "COM", "MEC", "INS", "ELE", "MOV", "AUT", "OUTRAS"]
    gpm_input = st.sidebar.selectbox("GPM", options=gpm_options, index=gpm_options.index(st.session_state["gpm_input"]) if st.session_state["gpm_input"] in gpm_options else 0, key="gpm_input")
    planejador_input = st.sidebar.text_input("Planejador", value=st.session_state["planejador_input"], key="planejador_input")
    status_options = ["Em planejamento", "AR", "Doc CQ", "IBTUG", "Materiais", "Definição MA", "SMS", "Outros", "Proposta Pacotes", "Concluído"]
    status_input = st.sidebar.multiselect("Status", options=status_options, key="status_input")
    info_input = st.sidebar.text_area("Informações", value=st.session_state["info_input"], key="info_input")
    
    if st.sidebar.button("Salvar Atualização"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_str = ", ".join(status_input)
        df_status = load_data()
        if ordem.strip() in df_status["Ordem"].astype(str).str.strip().values:
            idx = df_status[df_status["Ordem"].astype(str).str.strip() == ordem.strip()].index[0]
            df_status.at[idx, "Serviço_prioriza"] = servico_input
            df_status.at[idx, "GPM"] = gpm_input
            df_status.at[idx, "Planejador"] = planejador_input
            df_status.at[idx, "Status"] = status_str
            df_status.at[idx, "Informações"] = info_input
            df_status.at[idx, "Última Atualização"] = now
            st.sidebar.success("Ordem atualizada com sucesso!")
        else:
            new_row = pd.DataFrame({
                "Ordem": [ordem.strip()],
                "Serviço_prioriza": [servico_input],
                "GPM": [gpm_input],
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
st.subheader("Visualização de Ordens")

# Filtro de GPM na área principal
gpm_filter_options = ["CAL", "COM", "MEC", "INS", "ELE", "MOV", "AUT", "OUTRAS"]
selected_gpm = st.multiselect("Selecione GPM", options=gpm_filter_options, key="gpm_filter_main")

df_status = load_data()
df_final = df_status.copy()
colunas_desejadas = ["Ordem", "Serviço_prioriza", "GPM", "Planejador", "Status", "Informações", "Última Atualização"]
df_final = df_final[colunas_desejadas]
df_final = df_final.rename(columns={
    "Serviço_prioriza": "Serviço",
    "Status": "Serviço_status",
    "Última Atualização": "ultima atualização",
    "Informações": "informações"
})

if selected_gpm:
    df_final = df_final[df_final["GPM"].isin(selected_gpm)]
    
st.dataframe(df_final, use_container_width=True, height=600)
