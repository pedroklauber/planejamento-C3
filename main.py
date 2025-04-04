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
for key, default in {
    "ordem_input": "",
    "last_ordem": "",
    "servico_input": "",
    "gpm_input": "CAL",
    "planejador_input": "",
    "status_input": ["Em planejamento"],
    "info_input": "",
    "confirm_delete": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- FUNÇÃO PARA LIMPAR OS CAMPOS ---
def clear_all():
    st.session_state.clear()
    st.rerun()

# --- SIDEBAR ---
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
            st.session_state["servico_input"] = df.at[idx, "Serviço"] or ""
            st.session_state["gpm_input"] = (
                df.at[idx, "GPM"] if df.at[idx, "GPM"] in gpm_options else "CAL"
            )
            st.session_state["planejador_input"] = df.at[idx, "Planejador"] or ""
            st.session_state["status_input"] = (
                [s.strip() for s in df.at[idx, "Status"].split(",")] if pd.notna(df.at[idx, "Status"]) else [status_options[0]]
            )
            st.session_state["info_input"] = df.at[idx, "Informações"] or ""
            st.session_state["last_ordem"] = ordem
    st.sidebar.info("Se a ordem não existir, insira os dados para uma nova ordem.")

# Widgets do formulário
servico_input = st.sidebar.text_input("Serviço", key="servico_input")
gpm_index = gpm_options.index(st.session_state["gpm_input"]) if st.session_state["gpm_input"] in gpm_options else 0
gpm_input = st.sidebar.selectbox("GPM", options=gpm_options, index=gpm_index, key="gpm_input")
planejador_input = st.sidebar.text_input("Planejador", key="planejador_input")
status_input = st.sidebar.multiselect("Status", options=status_options, key="status_input")
info_input = st.sidebar.text_area("Informações", key="info_input")

# Botão para limpar dados
if st.sidebar.button("Limpar dados"):
    clear_all()

# Botão para salvar/atualizar a ordem
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
    st.rerun()

# Botão para apagar a ordem
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
        st.rerun()
    if col2.button("Não", key="delete_no"):
        st.sidebar.info("Exclusão cancelada.")
        st.session_state["confirm_delete"] = False

# --- ÁREA PRINCIPAL: VISUALIZAÇÃO ---
st.header("Planejamento de Ordens")
filtro_ordem = ordem.strip() if ordem else None
df = load_data()
colunas_ordem = ["Ordem", "Serviço", "GPM", "Planejador", "Status", "Informações", "Última Atualização"]
df = df[colunas_ordem]
if filtro_ordem:
    df = df[df["Ordem"].astype(str).str.strip() == filtro_ordem]
st.dataframe(df, use_container_width=True, height=600)
