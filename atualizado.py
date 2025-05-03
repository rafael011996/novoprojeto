import pandas as pd
import streamlit as st

st.set_page_config(page_title="Consultas TRIUNFANTE", layout="wide")

# Funções para carregar os dados
@st.cache_data(ttl=0)
def carregar_dados_entradas():
    url = 'https://raw.githubusercontent.com/rafael011996/novoprojeto/main/consultaentrada.csv'
    return pd.read_csv(url, delimiter=';', encoding='utf-8')

@st.cache_data(ttl=0)
def carregar_dados_produtos():
    url = 'https://raw.githubusercontent.com/rafael011996/novoprojeto/main/produtos.csv'
    return pd.read_csv(url, delimiter=';', encoding='utf-8')


# Interface do app
st.title("Consultas TRIUNFANTE")

abas = st.tabs(["📥 Consulta de Entradas", "📦 Consulta de Produtos"])

# Aba: Consulta de Entradas
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

# Aba: Consulta de Produtos
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
