import pandas as pd
import streamlit as st
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="Consultas TRIUNFANTE", layout="wide")

# IDs das planilhas
sheet_id_cargas_tcg = '1TKCyEJ76ESHNTuczB0wMrnc_8z8j3_1LmR6Z9VnlZ7E'

# Função genérica para carregar abas específicas
@st.cache_data(ttl=0)
def carregar_dados_google_sheet(sheet_id, aba):
    aba_codificada = urllib.parse.quote(aba, safe='')
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={aba_codificada}'
    return pd.read_csv(url)

@st.cache_data(ttl=0)
def carregar_dados_cargas(sheet_id, abas):
    frames = []
    for aba in abas:
        try:
            df = carregar_dados_google_sheet(sheet_id, aba)
            df['ABA'] = aba
            frames.append(df)
        except Exception as e:
            st.warning(f"Erro ao carregar aba {aba}: {e}")
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# Interface Streamlit
st.title("🚚 Consulta de Cargas TCG por Data")

# Carrega os dados
abas_meses = ['ABRIL/2025', 'MAIO/2025']
dados_cargas = carregar_dados_cargas(sheet_id_cargas_tcg, abas_meses)

if dados_cargas.empty:
    st.error("Não foi possível carregar os dados de cargas.")
else:
    # Normaliza colunas
    dados_cargas.columns = [col.strip().upper() for col in dados_cargas.columns]

    # Converte coluna de data, se existir
    if 'DATA' in dados_cargas.columns:
        dados_cargas['DATA'] = pd.to_datetime(dados_cargas['DATA'], dayfirst=True, errors='coerce')

        # Input de data
        data_selecionada = st.date_input("Selecione uma data para consultar as cargas:")

        # Filtra por data
        resultado = dados_cargas[dados_cargas['DATA'].dt.date == data_selecionada]

        if not resultado.empty:
            st.success(f"{len(resultado)} registro(s) encontrado(s) para a data {data_selecionada.strftime('%d/%m/%Y')}")
            st.dataframe(resultado)
        else:
            st.warning("Nenhuma carga encontrada para essa data.")
    else:
        st.error("A coluna 'DATA' não foi encontrada nos dados carregados.")
