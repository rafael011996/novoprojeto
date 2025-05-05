import pandas as pd
import streamlit as st

st.set_page_config(page_title="Consultas TRIUNFANTE", layout="wide")

# IDs das planilhas
sheet_id_cargas_tcg = '1TKCyEJ76ESHNTuczB0wMrnc_8z8j3_1LmR6Z9VnlZ7E'
sheet_id_cargas_mcd = '1xlc9vqgg6PwqMAu7-pzQ1VM_ElxDqGNPYFWk8zRXuiE'

# Título e abas
st.title("Consultas TRIUNFANTE")
abas = st.tabs(["\U0001F4E5 Consulta de Entradas", "\U0001F4E6 Consulta de Produtos", "\U0001F69A Consulta de Cargas"])

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
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# Aba 1: Entradas
with abas[0]:
    st.subheader("Consulta de Entradas")
    dados_entradas = carregar_dados_entradas()
    dados_entradas = dados_entradas[['Nota', 'Emissao', 'Dt.Cont.', 'CGC/CPF', 'Razao', 'Valor da Nota']]

    consulta_entrada = st.text_input('Digite o Código, Razão ou CPF/CNPJ da NF:', key="entrada")
    if consulta_entrada:
        resultado = dados_entradas[dados_entradas.apply(lambda row:
            consulta_entrada.lower() in str(row['Nota']).lower() or  
            consulta_entrada.lower() in str(row['Razao']).lower() or                                 
            consulta_entrada.lower() in str(row['CGC/CPF']).lower(), axis=1)]

        if not resultado.empty:
            st.write('Resultados encontrados:')
            st.dataframe(resultado)
        else:
            st.warning('Nenhum resultado encontrado.')

# Aba 2: Produtos
with abas[1]:
    st.subheader("Consulta de Produtos")
    dados_produtos = carregar_dados_produtos()
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
    else:
        abas_meses = ['04/ABRIL', '05/MAIO']
        sheet_id = sheet_id_cargas_mcd

    if num_carga:
        dados_cargas = carregar_dados_cargas(sheet_id, abas_meses)

        if dados_cargas.empty:
            st.error("Nenhuma carga encontrada ou erro ao carregar planilha.")
        else:
            try:
                if tipo_carga == "CARGAS TCG":
                    dados_cargas = dados_cargas.dropna(thresh=9)
                    resultado = dados_cargas[dados_cargas.iloc[:, 3].astype(str).str.contains(num_carga, na=False)]
                    colunas_exibir = dados_cargas.columns[2:9]

                elif tipo_carga == "CARGAS MCD":
                    dados_cargas = dados_cargas[dados_cargas.iloc[:, 4] != 'ID CARGA']
                    dados_cargas = dados_cargas.reset_index(drop=True)

                    if dados_cargas.shape[1] >= 1:
                        resultado = dados_cargas[dados_cargas.iloc[:, 4].astype(str).str.contains(num_carga, na=False)]
                        colunas_exibir = dados_cargas.columns[1:11]
                    else:
                        st.warning("A planilha MCD não tem colunas suficientes para a consulta.")
                        resultado = pd.DataFrame()

                if not resultado.empty:
                    st.success("Resultado da consulta:")
                    st.dataframe(resultado.loc[:, colunas_exibir])
                else:
                    st.warning("Nenhuma carga encontrada com esse número.")

            except Exception as e:
                st.error(f"Erro ao processar dados da planilha: {e}")
    else:
        st.info("Digite o número da carga para iniciar a consulta.")
