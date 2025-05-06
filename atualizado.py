import pandas as pd
import streamlit as st

st.set_page_config(page_title="Consultas TRIUNFANTE", layout="wide")

# IDs das planilhas
sheet_id_cargas_tcg = '1TKCyEJ76ESHNTuczB0wMrnc_8z8j3_1LmR6Z9VnlZ7E'
sheet_id_cargas_mcd = '1xlc9vqgg6PwqMAu7-pzQ1VM_ElxDqGNPYFWk8zRXuiE'
sheet_id_cargas_dev = '1pUFv1VzcOI9-u0miYW1lfqDMlKHUbo0S2lq62GG3KtQ'

# Título e abas
st.title("Consultas TRIUNFANTE")
abas = st.tabs([
    "📥 Consulta de Entradas", 
    "📦 Consulta de Produtos TCG E MCD", 
    "🚚 Consulta de Cargas", 
    "📥 MOTIVOS DE DEVOLUÇÕES"
])

# Funções de carregamento
@st.cache_data(ttl=0)
def carregar_dados_entradas():
    url = 'https://raw.githubusercontent.com/rafael011996/consultaentrada/main/consultaentrada.csv'
    return pd.read_csv(url, delimiter=';', encoding='utf-8')

@st.cache_data(ttl=0)
def carregar_dados_produtos():
    url = 'https://raw.githubusercontent.com/rafael011996/consulta/main/produtos.csv'
    return pd.read_csv(url, delimiter=';', encoding='utf-8')

@st.cache_data(ttl=0)
def carregar_dados_cargas(sheet_id, abas):
    frames = []
    for aba in abas:
        try:
            url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={aba}'
            df = pd.read_csv(url)
            df['ABA'] = aba
            frames.append(df)
        except Exception as e:
            st.warning(f"Erro ao carregar aba {aba}: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# Aba 1: Entradas
with abas[0]:
    st.subheader("Consulta de Entradas")
    dados_entradas = carregar_dados_entradas()
    if not dados_entradas.empty:
        dados_entradas = dados_entradas[['Nota', 'Emissao', 'Dt.Cont.', 'CGC/CPF', 'Razao', 'Valor da Nota']]
        consulta_entrada = st.text_input('Digite o Código, Razão ou CPF/CNPJ da NF:', key="entrada")
        if consulta_entrada:
            resultado = dados_entradas[dados_entradas.apply(
                lambda row: consulta_entrada.lower() in str(row['Nota']).lower(), axis=1)]
            if not resultado.empty:
                st.write('Resultados encontrados:')
                st.dataframe(resultado)
            else:
                st.warning('Nenhum resultado encontrado.')
    else:
        st.error("Erro ao carregar dados de entradas.")

# Aba 2: Produtos
with abas[1]:
    st.subheader("Consulta de Produtos")
    dados_produtos = carregar_dados_produtos()
    if not dados_produtos.empty:
        dados_produtos = dados_produtos[['Produto', 'Produto Fornecedor', 'Descricao', 'Codigo Getin', 'Saldo', 'Multiplo', 'Fator Conversao', 'Data Ult. Compra', 'NCM', 'CEST', '% IPI']]
        consulta_produto = st.text_input('Digite o nome, código ou descrição do produto:', key="produto")
        if consulta_produto:
            resultado = dados_produtos[dados_produtos.apply(lambda row:
                consulta_produto.lower() in str(row['Produto']).lower() or
                consulta_produto.lower() in str(row['Descricao']).lower() or
                consulta_produto.lower() in str(row['Codigo Getin']).lower() or
                consulta_produto.lower() in str(row['Produto Fornecedor']).lower(), axis=1)]
            if not resultado.empty:
                st.write('Resultados encontrados:')
                st.dataframe(resultado)
            else:
                st.warning('Nenhum produto encontrado.')
    else:
        st.error("Erro ao carregar dados de produtos.")

# Aba 3: Cargas
with abas[2]:
    st.subheader("Consulta de Cargas")

    col1, col2 = st.columns([1, 3])
    with col1:
        tipo_carga = st.radio("Tipo de carga:", ["CARGAS TCG", "CARGAS MCD"], horizontal=True)
    with col2:
        num_carga = st.text_input("Digite o número da carga:", key="carga")

    if tipo_carga == "CARGAS TCG":
        abas_meses = ['ABRIL/2025', 'MAIO/2025']
        sheet_id = sheet_id_cargas_tcg
        colunas_exibir_tcg = [2, 3, 4, 5, 6, 7, 8]
    else:
        abas_meses = ['04/ABRIL', '05/MAIO']
        sheet_id = sheet_id_cargas_mcd
        colunas_exibir_mcd = [4]

    dados_cargas = carregar_dados_cargas(sheet_id, abas_meses)

    if dados_cargas.empty:
        st.error("Erro ao carregar dados de cargas.")
    elif num_carga:
        if tipo_carga == "CARGAS MCD":
            resultado = dados_cargas[dados_cargas.iloc[:, 4].astype(str).str.contains(num_carga, na=False)]
            if not resultado.empty:
                st.success("Resultado da consulta:")
                try:
                    st.dataframe(resultado.iloc[:, colunas_exibir_mcd])
                except IndexError as e:
                    st.error(f"Erro ao exibir colunas: {e}")
                    st.write("Colunas disponíveis no resultado:")
                    st.write(resultado.columns.tolist())
            else:
                st.warning("Nenhuma carga encontrada com esse número.")
        elif tipo_carga == "CARGAS TCG":
            resultado = dados_cargas[dados_cargas.iloc[:, 3].astype(str).str.contains(num_carga, na=False)]
            if not resultado.empty:
                st.success("Resultado da consulta:")
                st.dataframe(resultado.iloc[:, colunas_exibir_tcg])
            else:
                st.warning("Nenhuma carga encontrada com esse número.")
    else:
        st.info("Digite o número da carga para iniciar a consulta.")

# Aba 4: Motivos de Devoluções
with abas[3]:
    st.subheader("Consulta por Código de Devolução")

    codigo_busca = st.text_input("Digite o código de devolução:", key="codigo_devolucao")
    
    if codigo_busca:
        aba_motivos = '📥 MOTIVOS DE DEVOLUÇÕES'
        dados_motivos = carregar_dados_cargas(sheet_id_cargas_dev, [aba_motivos])

        if dados_motivos.empty:
            st.error("Erro ao carregar dados da aba")
