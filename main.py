import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# --- CONFIGURAÇÃO DO SUPABASE ---
supabase_url = st.secrets["supabase"]["SUPABASE_URL"]
supabase_key = st.secrets["supabase"]["SUPABASE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)

# --- FUNÇÕES DE ACESSO AO BANCO DE DADOS (TABELA "ordens_status") ---
def load_data_supabase():
    response = supabase.table("ordens_status").select("*").execute()
    data = response.data if response.data is not None else []
    df = pd.DataFrame(data)
    if not df.empty:
        df.columns = df.columns.str.strip()
    return df

def save_data_supabase(record):
    # Upsert: insere ou atualiza com base na chave "Ordem"
    response = supabase.table("ordens_status").upsert(record, on_conflict="Ordem").execute()
    return response

def delete_data_supabase(ordem):
    response = supabase.table("ordens_status").delete().eq("Ordem", ordem).execute()
    return response


# --- ESTADO DA SESSÃO (INICIALIZAÇÃO) ---
for key, default in [
    ("ordem_input", ""),
    ("last_ordem", ""),
    ("servico_input", ""),
    ("gpm_input", "CAL"),
    ("planejador_input", ""),
    ("status_input", ["Em planejamento"]),
    ("info_input", ""),
    ("confirm_delete", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- SIDEBAR: CADASTRO/ATUALIZAÇÃO ---
st.sidebar.header("Atribuir Ordem")
ordem = st.sidebar.text_input("Número da Ordem", key="ordem_input")

status_options = [
    "Em planejamento", "AR", "Doc CQ", "IBTUG", "Materiais",
    "Definição MA", "SMS", "Outros", "Proposta Pacotes", "Concluído"
]
gpm_options = ["CAL", "COM", "MEC", "INS", "ELE", "MOV", "AUT", "OUTRAS"]

# Se uma ordem for digitada, pré-carrega os dados existentes do Supabase
if ordem:
    df = load_data_supabase()
    if ordem.strip() in df["Ordem"].astype(str).str.strip().values:
        idx = df[df["Ordem"].astype(str).str.strip() == ordem.strip()].index[0]
        if st.session_state["last_ordem"] != ordem:
            st.session_state["servico_input"] = df.at[idx, "Serviço"] if pd.notna(df.at[idx, "Serviço"]) else ""
            st.session_state["gpm_input"] = (
                df.at[idx, "GPM"] if pd.notna(df.at[idx, "GPM"]) and df.at[idx, "GPM"] in gpm_options else "CAL"
            )
            st.session_state["planejador_input"] = df.at[idx, "Planejador"] if pd.notna(df.at[idx, "Planejador"]) else ""
            st.session_state["status_input"] = (
                [s.strip() for s in df.at[idx, "Status"].split(",")] if pd.notna(df.at[idx, "Status"]) else [status_options[0]]
            )
            st.session_state["info_input"] = df.at[idx, "Informações"] if pd.notna(df.at[idx, "Informações"]) else ""
            st.session_state["last_ordem"] = ordem
    st.sidebar.info("Se a ordem não existir, insira os dados para uma nova ordem.")

# Criação dos widgets (os valores serão lidos automaticamente do st.session_state via key)
servico_input = st.sidebar.text_input("Serviço", key="servico_input")
if st.session_state["gpm_input"] in gpm_options:
    gpm_index = gpm_options.index(st.session_state["gpm_input"])
else:
    gpm_index = 0
gpm_input = st.sidebar.selectbox("GPM", options=gpm_options, index=gpm_index, key="gpm_input")
planejador_input = st.sidebar.text_input("Planejador", key="planejador_input")
status_input = st.sidebar.multiselect("Status", options=status_options, key="status_input")
info_input = st.sidebar.text_area("Informações", key="info_input")

# Botão para limpar os dados
if st.sidebar.button("Limpar dados"):
    # Redireciona para a mesma página com o parâmetro de query "clear=true"
    st.experimental_set_query_params(clear="true")
    st.experimental_rerun()

# Botão para salvar/atualizar a ordem
if st.sidebar.button("Salvar Atualização"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status_str = ", ".join(status_input)
    record = {
        "Ordem": ordem.strip(),
        "Serviço": servico_input,
        "GPM": gpm_input,
        "Planejador": planejador_input,
        "Status": status_str,
        "Informações": info_input,
        "Última Atualização": now
    }
    # Realiza o upsert no Supabase
    save_data_supabase(record)
    st.sidebar.success("Ordem salva com sucesso!")
    st.experimental_rerun()

# Botão para apagar a ordem (com confirmação)
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
filtro_ordem = ordem.strip() if ordem else None
df = load_data_supabase()
# Reordena as colunas conforme desejado
colunas_ordem = ["Ordem", "Serviço", "GPM", "Planejador", "Status", "Informações", "Última Atualização"]
df = df[colunas_ordem]
if filtro_ordem:
    df = df[df["Ordem"].astype(str).str.strip() == filtro_ordem]
st.dataframe(df, use_container_width=True, height=600)
