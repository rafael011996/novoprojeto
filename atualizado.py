import pandas as pd 
import streamlit as st
import urllib.parse
from datetime import datetime

st.set_page_config(page_title="Consultas TRIUNFANTE", layout="wide")

# IDs das planilhas
sheet_id_entradas = '1zk3sp8dazVU4qx_twI7oUe6l7ggTKzSkEmxAcYpoxqk'
sheet_id_cargas_tcg = '1TKCyEJ76ESHNTuczB0wMrnc_8z8j3_1LmR6Z9VnlZ7E'
sheet_id_cargas_mcd = '1xlc9vqgg6PwqMAu7-pzQ1VM_ElxDqGNPYFWk8zRXuiE'
sheet_id_cargas_dev = '1pUFv1VzcOI9-u0miYW1lfqDMlKHUbo0S2lq62GG3KtQ'
sheet_id_pedidos = '1xlJhN6PRrd297dkKbxz9W9TVL_-HK5UeGjuKxm8-Rbg'
sheet_id_produtos = '1PzkzkHwT5vv4u71KCNXpF-TFClzYKNngWHg13_wOR6o'

# Funções de carregamento
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

# Título e abas
st.title("Consultas TRIUNFANTE")
abas = st.tabs([
    "📥 Consulta de Entradas",
    "📦 Consulta de Produtos TCG E MCD",
    "🚚 Consulta de Cargas",
    "📥 MOTIVOS DE DEVOLUÇÕES",
    "🧾 Consulta de Pedidos"
])

# Aba 1: Consulta de Entradas
with abas[0]:
    st.subheader("Consulta de Entradas")
    st.success("Planilha de entradas carregada com sucesso.")
    try:
        dados_entradas = carregar_dados_google_sheet(sheet_id_entradas, 'Página1')
        consulta_nota = st.text_input('Digite o número da Nota:', key="nota")
        if consulta_nota:
            resultado = dados_entradas[dados_entradas['Nota'].astype(str) == consulta_nota.strip()]
            if not resultado.empty:
                st.dataframe(resultado)
            else:
                st.warning("Nenhum resultado encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar dados de entradas: {e}")

# Aba 2: Consulta de Produtos
with abas[1]:
    st.subheader("Consulta de Produtos")
    st.success("Planilha de produtos carregada com sucesso.")
    dados_produtos = carregar_dados_google_sheet(sheet_id_produtos, 'Página1')

    if not dados_produtos.empty:
        dados_produtos = dados_produtos[[
            'Produto', 'Produto Fornecedor', 'Descricao', 'Codigo Getin', 'Saldo',
            'Multiplo', 'Fator Conversao', 'Data Ult. Compra', 'NCM', 'CEST', '% IPI'
        ]]
        consulta_produto = st.text_input('Digite o nome, código ou descrição do produto:', key="produto")
        if consulta_produto:
            resultado = dados_produtos[dados_produtos.apply
                lambda row: consulta_produto.lower() in str(row).lower(), axis=1)]
            st.dataframe(resultado if not resultado.empty else "Nenhum produto encontrado.")
        else:
            st.error("Erro ao carregar dados de produtos.")

# Aba 3: Consulta de Cargas (com filtro por data adicionado)
with abas[2]:
    st.subheader("Consulta de Cargas")
    st.success("Planilha de cargas carregada com sucesso.")
    
    tipo = st.radio("Tipo de carga:", ["CARGAS TCG", "CARGAS MCD"], horizontal=True)
    dados_cargas = cargas_tcg if tipo == "CARGAS TCG" else cargas_mcd

# Conversão segura da coluna DATA
    if 'DATA' in dados_cargas.columns:
        dados_cargas['DATA'] = 
        dados_cargas['DATA']
        .astype(str)
        .str.replace(r'(\d{2})/(\d{2})/(\d{2})$', r'\1/\2/20\3', regex=True)
        dados_cargas['DATA'] = pd.to_datetime(dados_cargas['DATA'], dayfirst=True, errors='coerce')

# Filtros
       col1, col2 = st.columns([2, 3])

with col1:
    filtro_numero = st.text_input("Digite o número da carga:")

with col2:
    usar_data = st.checkbox("Filtrar por data?")
    filtro_data = st.date_input("Filtrar por data:", datetime.date.today()) if usar_data else None

# Aplicar filtros
filtro = dados_cargas.copy()

     if filtro_numero:
        filtro = filtro[filtro['ID CARGAS'].astype(str).str.contains(filtro_numero)]

     if usar_data and 'DATA' in filtro.columns:
        filtro = filtro[filtro['DATA'].dt.date == filtro_data]

# Exibir resultados
     if filtro.empty:
        st.warning("Nenhuma carga encontrada com os filtros aplicados.")
     else:
        st.dataframe(filtro, use_container_width=True)

# Aba 4: Motivos de Devoluções
with abas[3]:
    st.subheader("Consulta de Motivos de Devoluções")
    st.success("Planilha de devoluções carregada com sucesso.")
    dados_motivos = carregar_dados_cargas(sheet_id_cargas_dev, ["📥 MOTIVOS DE DEVOLUÇÕES"])
    if dados_motivos.empty:
        st.error("Erro ao carregar dados da aba de devoluções.")
    else:
        consulta_codigo = st.text_input("Digite o código de devolução (coluna J):", key="codigo_dev")
        if consulta_codigo:
            resultado = dados_motivos[dados_motivos.iloc[:, 9].astype(str).str.contains(consulta_codigo, na=False)]
            colunas_exibir = list(resultado.columns[:9])
            st.dataframe(resultado[colunas_exibir] if not resultado.empty else "Nenhum resultado encontrado.")

# Aba 5: Consulta de Pedidos
with abas[4]:
    st.subheader("Consulta de Pedidos")
    try:
        dados_pedidos = carregar_dados_google_sheet(sheet_id_pedidos, 'Página1')
        st.success("Planilha de pedidos carregada com sucesso.")

        col1, col2 = st.columns(2)
        with col1:
            repr_input = st.text_input("Digite o código do Representante (Repr):", key="repr")
        with col2:
            pedido_input = st.text_input("Digite o número do Pedido:", key="pedido")

        if repr_input and pedido_input:
            resultado = dados_pedidos[
                (dados_pedidos['Repr'].astype(str) == repr_input.strip()) &
                (dados_pedidos['Pedido'].astype(str) == pedido_input.strip())
            ]
            st.dataframe(resultado if not resultado.empty else "Nenhum pedido encontrado com esses dados.")

    except Exception as e:
        st.error(f"Erro ao carregar pedidos: {e}")
