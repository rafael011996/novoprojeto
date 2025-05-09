import pandas as pd
import streamlit as st
import urllib.parse

st.set_page_config(page_title="Consultas TRIUNFANTE", layout="wide")

# IDs das planilhas
sheet_id_entradas = '1zk3sp8dazVU4qx_twI7oUe6l7ggTKzSkEmxAcYpoxqk'
sheet_id_cargas_tcg = '1TKCyEJ76ESHNTuczB0wMrnc_8z8j3_1LmR6Z9VnlZ7E'
sheet_id_cargas_mcd = '1xlc9vqgg6PwqMAu7-pzQ1VM_ElxDqGNPYFWk8zRXuiE'
sheet_id_cargas_dev = '1pUFv1VzcOI9-u0miYW1lfqDMlKHUbo0S2lq62GG3KtQ'
sheet_id_pedidos = '1xlJhN6PRrd297dkKbxz9W9TVL_-HK5UeGjuKxm8-Rbg'
sheet_id_produtos = '1PzkzkHwT5vv4u71KCNXpF-TFClzYKNngWHg13_wOR6o'
sheet_id_produtosmcd = '1dxvHYgcC8x53li2vCmVY8VVlighWSa4dAjHx7gQPF-0'

st.title("Consultas TRIUNFANTE")

abas = st.tabs([
    "📥 Consulta de Entradas TCG e MCD",
    "📦 Consulta de Produtos TCG",
    "📦 Consulta de Produtos MCD",
    "🚚 Consulta de Cargas",
    "📥 MOTIVOS DE DEVOLUÇÕES TCG e MCD",
    "🧾 Consulta de Pedidos TCG e MCD"
])

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

# Aba 1: Consulta de Entradas
with abas[0]:
    st.subheader("Consulta de Entradas")
    try:
        dados_entradas = carregar_dados_google_sheet(sheet_id_entradas, 'Página1')
        st.success("Planilha de entradas carregada com sucesso.")
        consulta_nota = st.text_input('Digite o número da Nota:', key="nota")
        if consulta_nota:
            resultado = dados_entradas[dados_entradas['Nota'].astype(str) == consulta_nota.strip()]
            if not resultado.empty:
                st.dataframe(resultado)
            else:
                st.warning("Nenhum resultado encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar dados de entradas: {e}")

# Aba 2: Produtos TCG
with abas[1]:
    st.subheader("Consulta de Produtos TCG")
    dados_produtos = carregar_dados_google_sheet(sheet_id_produtos, 'Página1')
    if not dados_produtos.empty:
        st.success("Planilha de produtos carregada com sucesso.")
        dados_produtos = dados_produtos[['Produto', 'Produto Fornecedor', 'Descricao', 'Codigo Getin', 'Saldo', 'Multiplo', 'Fator Conversao', 'Data Ult. Compra', 'NCM', 'CEST', '% IPI']]
        consulta_produto = st.text_input('Digite o nome, código ou descrição do produto:', key="produto_tcg")
        if consulta_produto:
            resultado = dados_produtos[dados_produtos.apply(lambda row: consulta_produto.lower() in str(row).lower(), axis=1)]
            if not resultado.empty:
                st.dataframe(resultado)
            else:
                st.warning("Nenhum produto encontrado.")
    else:
        st.error("Erro ao carregar dados de produtos.")

# Aba 3: Produtos MCD
with abas[2]:
    st.subheader("Consulta de Produtos MCD")
    dados_produtos = carregar_dados_google_sheet(sheet_id_produtosmcd, 'Página1')
    if not dados_produtos.empty:
        st.success("Planilha de produtos carregada com sucesso.")
        dados_produtos = dados_produtos[['Produto', 'Produto Fornecedor', 'Descricao', 'Codigo Getin', 'Saldo', 'Multiplo', 'Fator Conversao', 'Data Ult. Compra', 'NCM', 'CEST', '% IPI']]
        consulta_produto = st.text_input('Digite o nome, código ou descrição do produto:', key="produto_mcd")
        if consulta_produto:
            resultado = dados_produtos[dados_produtos.apply(lambda row: consulta_produto.lower() in str(row).lower(), axis=1)]
            if not resultado.empty:
                st.dataframe(resultado)
            else:
                st.warning("Nenhum produto encontrado.")
    else:
        st.error("Erro ao carregar dados de produtos.")

# Aba 4: Consulta de Cargas
with abas[3]:
    st.subheader("Consulta de Cargas")
    col1, col2 = st.columns([1, 3])
    with col1:
        tipo_carga = st.radio("Tipo de carga:", ["CARGAS TCG", "CARGAS MCD"], horizontal=True)
    with col2:
        num_carga = st.text_input("Digite o número da carga:", key="carga")

    abas_meses = ['ABRIL/2025', 'MAIO/2025'] if tipo_carga == "CARGAS TCG" else ['04/ABRIL', '05/MAIO']
    sheet_id = sheet_id_cargas_tcg if tipo_carga == "CARGAS TCG" else sheet_id_cargas_mcd
    dados_cargas = carregar_dados_cargas(sheet_id, abas_meses)

    if dados_cargas.empty:
        st.error("Erro ao carregar dados de cargas.")
    elif num_carga:
        filtro = dados_cargas[dados_cargas.apply(lambda row: num_carga in str(row.values), axis=1)]
        if not filtro.empty:
            st.dataframe(filtro)
        else:
            st.warning("Nenhuma carga encontrada com esse número.")
    else:
        st.info("Digite o número da carga para iniciar a consulta.")

# Aba 5: Motivos de Devoluções
with abas[4]:
    st.subheader("Consulta de Motivos de Devoluções")
    dados_motivos = carregar_dados_cargas(sheet_id_cargas_dev, ["📥 MOTIVOS DE DEVOLUÇÕES"])
    if dados_motivos.empty:
        st.error("Erro ao carregar dados da aba de devoluções.")
    else:
        st.success("Planilha de devoluções carregada com sucesso.")
        consulta_codigo = st.text_input("Digite o código de devolução (coluna J):", key="codigo_dev")
        if consulta_codigo:
            codigo_completo = f"DEV-{numero_codigo.strip()}"
            resultado = dados_motivos[dados_motivos.iloc[:,9].astype(str).str.contains(consulta_codigo, na=False)]
            colunas_exibir = list(resultado.columns[:9])
            if not resultado.empty:
                st.dataframe(resultado[colunas_exibir])
            else:
                st.warning("Nenhum resultado encontrado.")

# Aba 6: Consulta de Pedidos
with abas[5]:
    st.subheader("Consulta de Pedidos")
    try:
        dados_pedidos = carregar_dados_google_sheet(sheet_id_pedidos, 'Página1')
        st.success("Planilha de pedidos carregada com sucesso.")
        col1, col2 = st.columns(2)
        with col1:
            repr_input = st.text_input("Digite o código do Representante:", key="repr")
        with col2:
            pedido_input = st.text_input("Digite o número do Pedido:", key="pedido")
        if repr_input and pedido_input:
            resultado = dados_pedidos[
                (dados_pedidos['Repr'].astype(str) == repr_input.strip()) &
                (dados_pedidos['Pedido'].astype(str) == pedido_input.strip())
            ]
            if not resultado.empty:
                st.dataframe(resultado)
            else:
                st.warning("Nenhum pedido encontrado com esses dados.")
    except Exception as e:
        st.error(f"Erro ao carregar pedidos: {e}")
