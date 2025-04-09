import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
import httpx
from supabase.lib.client_options import ClientOptions


# --- CONFIGURAÇÃO ---
st.set_page_config(layout="wide", page_title="Planejamento das Ordens")

# Conexão com Supabase
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)





status_options = ["Em planejamento", "AR", "Doc CQ", "IBTUG", "Materiais",
                  "Definição MA", "SMS", "Outros", "Proposta Pacotes", "Concluído"]

# --- FUNÇÕES ---

def load_data():
    response = supabase.table("ordens_status").select("*").execute()
    data = response.data if response.data else []
    df = pd.DataFrame(data)
    if not df.empty:
        df = df.astype(str)
    else:
        df = pd.DataFrame(columns=["ordem", "planejador", "status", "informacoes", "servico_prioriza", "gpm", "ultima_atualizacao"])
    return df

def save_data(df, ordem, update=False):
    if update:
        supabase.table("ordens_status").update(df).eq("ordem", ordem).execute()
    else:
        supabase.table("ordens_status").insert(df).execute()

def delete_data(ordem):
    supabase.table("ordens_status").delete().eq("ordem", ordem).execute()

# --- ESTADO DA SESSÃO ---
for key in ["ordem_input", "last_ordem", "planejador_input", "status_input",
            "info_input", "servico_prioriza_input", "gpm_input", "confirm_delete"]:
    if key not in st.session_state:
        st.session_state[key] = "" if key != "status_input" else ["Em planejamento"]
if not st.session_state["confirm_delete"]:
    st.session_state["confirm_delete"] = False

# --- SIDEBAR ---
st.sidebar.header("Atribuir Ordem")
ordem = st.sidebar.text_input("Número da Ordem", key="ordem_input")

if ordem:
    df_status_temp = load_data()
    if ordem.strip() in df_status_temp["ordem"].astype(str).str.strip().values:
        st.sidebar.info("Esta ordem já existe. Ao salvar, os dados serão atualizados.")

    def clear_fields():
        for key in ["ordem_input", "planejador_input", "status_input", "info_input", "servico_prioriza_input", "gpm_input", "last_ordem"]:
            st.session_state[key] = "" if key != "status_input" else ["Em planejamento"]
        st.experimental_rerun()

    st.sidebar.button("Limpar dados", on_click=clear_fields)

    # Carregar dados existentes
    df_status = load_data()
    ordem_df = df_status[df_status["ordem"].astype(str).str.strip() == ordem.strip()]
    if not ordem_df.empty:
        row = ordem_df.iloc[0]
        st.session_state["planejador_input"] = row["planejador"]
        st.session_state["status_input"] = [s.strip() for s in row["status"].split(",")] if row["status"] else ["Em planejamento"]
        st.session_state["info_input"] = row["informacoes"]
        st.session_state["servico_prioriza_input"] = row["servico_prioriza"]
        st.session_state["gpm_input"] = row["gpm"]

    planejador_input = st.sidebar.text_input("Planejador", value=st.session_state["planejador_input"], key="planejador_input")
    status_input = st.sidebar.multiselect("Status", options=status_options, default=st.session_state["status_input"], key="status_input")
    info_input = st.sidebar.text_area("Informações", value=st.session_state["info_input"], key="info_input")
    servico_prioriza_input = st.sidebar.text_input("Serviço Prioriza", value=st.session_state["servico_prioriza_input"], key="servico_prioriza_input")
    gpm_input = st.sidebar.text_input("GPM", value=st.session_state["gpm_input"], key="gpm_input")

    if st.sidebar.button("Salvar Atualização"):
        now = datetime.now().isoformat()
        status_str = ", ".join(status_input)
        data_dict = {
            "ordem": ordem.strip(),
            "planejador": planejador_input,
            "status": status_str,
            "informacoes": info_input,
            "servico_prioriza": servico_prioriza_input,
            "gpm": gpm_input,
            "ultima_atualizacao": now
        }

        is_update = ordem.strip() in df_status["ordem"].astype(str).str.strip().values
        save_data(data_dict, ordem.strip(), update=is_update)
        st.sidebar.success("Ordem atualizada!" if is_update else "Nova ordem inserida!")
        st.experimental_rerun()

    if st.sidebar.button("Apagar Ordem") and not st.session_state["confirm_delete"]:
        st.session_state["confirm_delete"] = True

    if st.session_state["confirm_delete"]:
        st.sidebar.write("Tem certeza que deseja apagar a ordem?")
        col1, col2 = st.sidebar.columns(2)
        if col1.button("Sim"):
            delete_data(ordem.strip())
            st.sidebar.success("Ordem apagada!")
            st.session_state["confirm_delete"] = False
            st.experimental_rerun()
        if col2.button("Não"):
            st.sidebar.info("Exclusão cancelada.")
            st.session_state["confirm_delete"] = False

# --- ÁREA PRINCIPAL ---
st.header("Planejamento de Ordens")
st.subheader("Filtro de GPM (visualização)")
df_status = load_data()

gpm_values = df_status["gpm"].dropna().unique().tolist()
selected_gpm = st.multiselect("Selecione GPM", options=gpm_values, key="gpm_filter_main")

df_final = df_status.copy()
df_final = df_final.rename(columns={
    "ordem": "Ordem",
    "planejador": "Planejador",
    "status": "Serviço_status",
    "informacoes": "informações",
    "servico_prioriza": "Serviço_prioriza",
    "gpm": "GPM",
    "ultima_atualizacao": "ultima atualização"
})

colunas_desejadas = ["Ordem", "Serviço_prioriza", "GPM", "Planejador", "Serviço_status", "informações", "ultima atualização"]
df_final = df_final[colunas_desejadas]

if selected_gpm:
    df_final = df_final[df_final["GPM"].isin(selected_gpm)]

if ordem:
    df_final = df_final[df_final["Ordem"].astype(str).str.strip() == ordem.strip()]

st.dataframe(df_final, use_container_width=True, height=600)
