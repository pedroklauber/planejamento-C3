#url = "https://jiranaejssohtmfydqbz.supabase.co"
#key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcmFuYWVqc3NvaHRtZnlkcWJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMxMTk2NTcsImV4cCI6MjA1ODY5NTY1N30.swAF_e2Chb4lePqXHwN7NjMbzPMVr8rok40ChdMJq2I"

import httpx
from supabase import create_client, Client
import os
os.environ["PYTHONHTTPSVERIFY"] = "0"

from supabase import create_client

# Substitua pelo caminho REAL do seu certificado .crt
cert_path = "petrobras_supabase.crt"

# Cria um cliente HTTP com o certificado customizado
http_client = httpx.Client(verify=cert_path)

# Dados de acesso ao Supabase
url = "https://jiranaejssohtmfydqbz.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppcmFuYWVqc3NvaHRtZnlkcWJ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMxMTk2NTcsImV4cCI6MjA1ODY5NTY1N30.swAF_e2Chb4lePqXHwN7NjMbzPMVr8rok40ChdMJq2I"


supabase = create_client(url, key)
response = supabase.table("ordens_status").select("*").execute()
print(response.data)