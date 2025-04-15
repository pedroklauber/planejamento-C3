# app.py  –  Planejamento de Ordens (Firestore + Streamlit)

import streamlit as st
import pandas as pd
import datetime as dt
import threading, queue
from pathlib import Path

# ────────────────────────────────────────────────
# 1. CONEXÃO FIREBASE
# ────────────────────────────────────────────────
import firebase_admin
from firebase_admin import credentials, firestore

CRED_PATH = Path(__file__).with_name("service_account.json")   # caminho da chave
COLLECTION = "ordens_status"                                  # nome da coleção

@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        cred = credentials.Certificate(CRED_PATH)
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = get_db()

# ────────────────────────────────────────────────
# 2. FUNÇÕES CRUD
# ────────────────────────────────────────────────
CAMPOS = ["Ordem","Planejador","Status","Informações",
          "Serviço_prioriza","GPM","Última Atualização"]

def linha_vazia():
    return {c:"" for c in CAMPOS}

def load_dataframe():
    try:
        docs = db.collection(COLLECTION).stream()
        rows = [d.to_dict() for d in docs]
        st.info(f"🔎 {len(rows)} documentos lidos do Firestore.")
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"❌ Erro ao consultar Firestore:\n{e}")
        raise            # faz o spinner parar


def salvar_linha(dados: dict):
    dados["Última Atualização"] = dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    doc = db.collection(COLLECTION).document(str(dados["Ordem"]).strip())
    doc.set(dados, merge=True)

def deletar_ordem(ordem: str):
    db.collection(COLLECTION).document(str(ordem).strip()).delete()

# ────────────────────────────────────────────────
# 3. LISTENER (tempo real)
# ────────────────────────────────────────────────
update_q = queue.Queue()

def listener():
    def _on_snapshot(col_snapshot, changes, _):
        update_q.put(True)
    db.collection(COLLECTION).on_snapshot(_on_snapshot)

threading.Thread(target=listener, daemon=True).start()

# ────────────────────────────────────────────────
# 4. CONFIG STREAMLIT
# ────────────────────────────────────────────────
st.set_page_config(page_title="Planejamento das Ordens", layout="wide")

status_options = ["Em planejamento","AR","Doc CQ","IBTUG","Materiais",
                  "Definição MA","SMS","Outros","Proposta Pacotes","Concluído"]

# ────────────────────────────────────────────────
# 5. SIDEBAR – Formulário
# ────────────────────────────────────────────────
st.sidebar.header("Atribuir / Atualizar Ordem")

ordem       = st.sidebar.text_input("Número da Ordem")
planejador  = st.sidebar.text_input("Planejador")
status_sel  = st.sidebar.multiselect("Status", status_options, default=["Em planejamento"])
info        = st.sidebar.text_area("Informações")
serv_prior  = st.sidebar.text_input("Serviço Prioriza")
gpm         = st.sidebar.text_input("GPM")

if st.sidebar.button("💾 Salvar"):
    if ordem.strip() == "":
        st.sidebar.error("Preencha o número da ordem.")
    else:
        salvar_linha({
            "Ordem": ordem.strip(),
            "Planejador": planejador,
            "Status": ", ".join(status_sel),
            "Informações": info,
            "Serviço_prioriza": serv_prior,
            "GPM": gpm
        })
        st.sidebar.success("Dados salvos!")
        st.cache_data.clear()

if st.sidebar.button("🗑️ Apagar") and ordem.strip():
    deletar_ordem(ordem)
    st.sidebar.success("Ordem apagada!")
    st.cache_data.clear()

# ────────────────────────────────────────────────
# 6. PRINCIPAL – Visualização
# ────────────────────────────────────────────────
# invalida cache se listener detectou mudança
if not update_q.empty():
    st.cache_data.clear()
    update_q.get()

@st.cache_data(ttl=5)
def get_df():
    return load_dataframe()

df = get_df()

st.header("Planejamento de Ordens")

# filtro por GPM
gpm_values = sorted([g for g in df["GPM"].dropna().unique() if g != ""])
sel_gpm = st.multiselect("Filtrar por GPM", gpm_values)
df_view = df.copy()
if sel_gpm:
    df_view = df_view[df_view["GPM"].isin(sel_gpm)]

st.dataframe(df_view[CAMPOS], use_container_width=True, height=600)

# download CSV
csv_bytes = df_view.to_csv(index=False).encode()
st.download_button("⬇️ Baixar CSV", csv_bytes, "ordens_export.csv", "text/csv")
