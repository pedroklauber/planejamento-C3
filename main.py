import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURAÇÃO E ARQUIVOS ---
st.set_page_config(layout="wide", page_title="Planejamento das Ordens")
CSV_FILE = "ordens_status.csv"

if not os.path.exists(CSV_FILE):
    pd.DataFrame(
        columns=["Ordem", "Serviço", "GPM", "Planejador", "Status", "Informações", "Última Atualização"]
    ).to_csv(CSV_FILE, index=False)

# --- FUNÇÕES DE LEITURA E SALVAMENTO ---
def load_data():
    df = pd.read_csv(CSV_FILE, dtype=str)
    df.columns = df.columns.str.strip()
    # Garante que as colunas "Serviço" e "GPM" existam
    for col in ["Serviço", "GPM"]:
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
if "status_input" not in st.session_state:
    st.session_state["status_input"] = ["Em planejamento"]
if "info_input" not in st.session_state:
    st.session_state["info_input"] = ""
if "confirm_delete" not in st.session_state:
    st.session_state["confirm_delete"] = False

# --- FUNÇÃO PARA LIMPAR OS CAMPOS ---
def clear_all():
    st.session_state["ordem_input"] = ""
    st.session_state["servico_input"] = ""
    st.session_state["gpm_input"] = "CAL"
    st.session_state["planejador_input"] = ""
    st.session_state["status_input"] = ["Em planejamento"]
    st.session_state["info_input"] = ""
    st.session_state["last_ordem"] = ""
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

# --- SIDEBAR: CADASTRO/ATUALIZAÇÃO ---
st.sidebar.header("Atribuir Ordem")
ordem = st.sidebar.text_input("Número da Ordem", key="ordem_input")

status_options = [
    "Em planejamento", "AR", "Doc CQ", "IBTUG", "Materiais",
    "Definição MA", "SMS", "Outros", "Proposta Pacotes", "Concluído"
]
gpm_options = ["CAL", "COM", "MEC", "INS", "ELE", "MOV", "AUT", "OUTRAS"]

if ordem:
    df = load_data()
    if ordem.strip() in df["Ordem"].astype(str).str.strip().values:
        idx = df[df["Ordem"].astype(str).str.strip() == ordem.strip()].index[0]
        if st.session_state["last_ordem"] != ordem:
            st.session_state["servico_input"] = df.at[idx, "Serviço"] if pd.notna(df.at[idx, "Serviço"]) else ""
            st.session_state["gpm_input"] = df.at[idx, "GPM"] if pd.notna(df.at[idx, "GPM"]) and df.at[idx, "GPM"] in gpm_options else "CAL"
            st.session_state["planejador_input"] = df.at[idx, "Planejador"] if pd.notna(df.at[idx, "Planejador"]) else ""
            st.session_state["status_input"] = (
                [s.strip() for s in df.at[idx, "Status"].split(",")] if pd.notna(df.at[idx, "Status"]) else [status_options[0]]
            )
            st.session_state["info_input"] = df.at[idx, "Informações"] if pd.notna(df.at[idx, "Informações"]) else ""
            st.session_state["last_ordem"] = ordem
    st.sidebar.info("Se a ordem não existir, insira os dados para uma nova ordem.")

# Widgets (os valores já estarão em st.session_state, então não usamos o parâmetro value)
servico_input = st.sidebar.text_input("Serviço", key="servico_input")
if st.session_state["gpm_input"] in gpm_options:
    gpm_index = gpm_options.index(st.session_state["gpm_input"])
else:
    gpm_index = 0
gpm_input = st.sidebar.selectbox("GPM", options=gpm_options, index=gpm_index, key="gpm_input")
planejador_input = st.sidebar.text_input("Planejador", key="planejador_input")
status_input = st.sidebar.multiselect("Status", options=status_options, key="status_input")
info_input = st.sidebar.text_area("Informações", key="info_input")

if st.sidebar.button("Limpar dados"):
    clear_all()

if st.sidebar.button("Salvar Atualização"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_str = ", ".join(status_input)
    df = load_data()
    if ordem.strip() in df["Ordem"].astype(str).str.strip().values:
        idx = df[df["Ordem"].astype(str).str.strip() == ordem.strip()].index[0]
        df.at[idx, "Serviço"] = servico_input
        df.at[idx, "GPM"] = gpm_input
        df.at[idx, "Planejador"] = planejador_input
        df.at[idx, "Status"] = status_str
        df.at[idx, "Informações"] = info_input
        df.at[idx, "Última Atualização"] = now
        st.sidebar.success("Ordem atualizada com sucesso!")
    else:
        new_row = pd.DataFrame({
            "Ordem": [ordem.strip()],
            "Serviço": [servico_input],
            "GPM": [gpm_input],
            "Planejador": [planejador_input],
            "Status": [status_str],
            "Informações": [info_input],
            "Última Atualização": [now]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        st.sidebar.success("Nova ordem inserida com sucesso!")
    save_data(df)
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

if st.sidebar.button("Apagar Ordem") and not st.session_state["confirm_delete"]:
    st.session_state["confirm_delete"] = True
if st.session_state["confirm_delete"]:
    st.sidebar.write("Tem certeza que deseja apagar a ordem?")
    col1, col2 = st.sidebar.columns(2)
    if col1.button("Sim", key="delete_yes"):
        df = load_data()
        if ordem.strip() in df["Ordem"].astype(str).str.strip().values:
            df = df[df["Ordem"].astype(str).str.strip() != ordem.strip()]
            save_data(df)
            st.sidebar.success("Ordem apagada com sucesso!")
        else:
            st.sidebar.error("Ordem não encontrada!")
        st.session_state["confirm_delete"] = False
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
    if col2.button("Não", key="delete_no"):
        st.sidebar.info("Exclusão cancelada.")
        st.session_state["confirm_delete"] = False

# --- ÁREA PRINCIPAL: VISUALIZAÇÃO ---
st.header("Planejamento de Ordens")
filtro_ordem = ordem.strip() if ordem else None
df = load_data()
if filtro_ordem:
    df = df[df["Ordem"].astype(str).str.strip() == filtro_ordem]
st.dataframe(df, use_container_width=True, height=600)
