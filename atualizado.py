import pandas as pd
import streamlit as st
import urllib.parse

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
def carregar_dados_csv(url):
    return pd.read_csv(url, delimiter=';', encoding='utf-8')

@st.cache_data(ttl=0)
def carregar_dados_cargas(sheet_id, abas):
    frames = []
    for aba in abas:
        try:
            aba_codificada = urllib.parse.quote(aba, safe='')
            url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={aba_codificada}'
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
# Aba 1: Consulta por Nota em planilha do Google
with abas[0]:
    st.subheader("Consulta por Nota Fiscal de ENTRADAS")
    
    # ID da nova planilha de entrada
    sheet_id_entrada_google = "1zk3sp8dazVU4qx_twI7oUe6l7ggTKzSkEmxAcYpoxqk"
    aba_nome = "Página1"  # ajuste se o nome da aba for diferente
    
    @st.cache_data(ttl=0)
    def carregar_dados_google_sheet(sheet_id, aba):
        aba_codificada = urllib.parse.quote(aba, safe='')
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={aba_codificada}'
        return pd.read_csv(url)

    try:
        dados_entrada_sheet = carregar_dados_google_sheet(sheet_id_entrada_google, aba_nome)
        st.success("Planilha carregada com sucesso.")
        
        nota_consulta = st.text_input("Digite o número da Nota Fiscal (coluna A):", key="nota_entrada")
        
        if nota_consulta:
            resultado = dados_entrada_sheet[dados_entrada_sheet.iloc[:, 0].astype(str) == nota_consulta]
            if not resultado.empty:
                st.dataframe(resultado)
            else:
                st.warning("Nenhuma nota encontrada com esse número.")
    except Exception as e:
        st.error(f"Erro ao carregar dados da planilha: {e}")


# Aba 2: Produtos
with abas[1]:
    st.subheader("Consulta de Produtos")
    url = 'https://raw.githubusercontent.com/rafael011996/consulta/main/produtos.csv'
    dados_produtos = carregar_dados_csv(url)

    if not dados_produtos.empty:
        dados_produtos = dados_produtos[['Produto', 'Produto Fornecedor', 'Descricao', 'Codigo Getin', 'Saldo', 'Multiplo', 'Fator Conversao', 'Data Ult. Compra', 'NCM', 'CEST', '% IPI']]
        consulta_produto = st.text_input('Digite o nome, código ou descrição do produto:', key="produto")
        if consulta_produto:
            resultado = dados_produtos[dados_produtos.apply(
                lambda row: consulta_produto.lower() in str(row).lower(), axis=1)]
            st.dataframe(resultado if not resultado.empty else "Nenhum produto encontrado.")
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
    else:
        abas_meses = ['04/ABRIL', '05/MAIO']
        sheet_id = sheet_id_cargas_mcd

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

# Aba 4: Motivos de Devoluções
with abas[3]:
    st.subheader("Consulta de Motivos de Devoluções")
    aba_motivos = ["📥 MOTIVOS DE DEVOLUÇÕES"]
    dados_motivos = carregar_dados_cargas(sheet_id_cargas_dev, aba_motivos)

    if dados_motivos.empty:
        st.error("Erro ao carregar dados da aba de devoluções.")
    else:
        consulta_codigo = st.text_input("Digite o código de devolução (coluna J):", key="codigo_dev")
        if consulta_codigo:
            resultado = dados_motivos[dados_motivos.iloc[:, 9].astype(str).str.contains(consulta_codigo, na=False)]
            if not resultado.empty:
                colunas_exibir = list(resultado.columns[:9])  # A até I
                st.dataframe(resultado[colunas_exibir])
            else:
                st.warning("Nenhum resultado encontrado para o código informado.")
