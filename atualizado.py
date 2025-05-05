import pandas as pd
import streamlit as st
import requests

st.set_page_config(page_title="Consultas TRIUNFANTE", layout="wide")

# URLs das planilhas
sheet_id_cargas = '1TKCyEJ76ESHNTuczB0wMrnc_8z8j3_1LmR6Z9VnlZ7E'  # <-- Substitua pelo ID real
sheet_url = f'https://docs.google.com/spreadsheets/d/1TKCyEJ76ESHNTuczB0wMrnc_8z8j3_1LmR6Z9VnlZ7E/edit?usp=sharing'

# Abas da interface
st.title("Consultas TRIUNFANTE")
abas = st.tabs(["📥 Consulta de Entradas", "📦 Consulta de Produtos", "🚚 Consulta de Cargas"])

# Entradas
@st.cache_data(ttl=0)
def carregar_dados_entradas():
    url = 'https://raw.githubusercontent.com/rafael011996/consultaentrada/main/consultaentrada.csv'
    return pd.read_csv(url, delimiter=';', encoding='utf-8')

# Produtos
@st.cache_data(ttl=0)
def carregar_dados_produtos():
    url = 'https://raw.githubusercontent.com/rafael011996/consulta/main/produtos.csv'
    return pd.read_csv(url, delimiter=';', encoding='utf-8')

# Cargas
@st.cache_data(ttl=0)
def carregar_dados_cargas(sheet_id):
    # Lista de abas conhecidas — você pode atualizar se mudar
    abas = ['Aba1', 'Aba2', 'Aba3']  # <-- Substitua com os nomes reais das abas
    frames = []
    for aba in abas:
        try:
            url = f'https://docs.google.com/spreadsheets/d/1TKCyEJ76ESHNTuczB0wMrnc_8z8j3_1LmR6Z9VnlZ7E/edit?usp=sharing'
            df = pd.read_csv(url)
            df['ABRIL/2025'] = aba  # Marcar de qual aba veio
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
    num_carga = st.text_input("Digite o número da carga:", key="carga")

    if num_carga:
        dados_cargas = carregar_dados_cargas(sheet_id_cargas)
        if dados_cargas.empty:
            st.error("Nenhuma carga encontrada ou erro ao carregar planilha.")
        else:
            resultado = dados_cargas[dados_cargas.iloc[:, 3].astype(str).str.contains(num_carga)]
            if not resultado.empty:
                st.write("Resultado da consulta:")
                st.dataframe(resultado.iloc[:, 4:9])  # Colunas E a I
            else:
                st.warning("Nenhuma carga encontrada com esse número.")
