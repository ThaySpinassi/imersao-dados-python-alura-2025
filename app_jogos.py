import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Vendas de Jogos",
    page_icon="🎮",
    layout="wide",
)

# --- Paleta global ---
PALETA = px.colors.qualitative.D3

# --- Carregamento dos dados ---
try:
    df = pd.read_csv("C:\\Users\\thayn\\Documents\\Análise de dados\\Alura - Dados\\Imersão Dados\\top_50_jogos.csv")
except FileNotFoundError:
    st.error("Erro: O arquivo 'top_50_jogos.csv' não foi encontrado. Verifique o caminho.")
    st.stop()

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro por Tipo de Gênero
generos_disponiveis = sorted(df["Gênero"].unique())
generos_selecionados = st.sidebar.multiselect("Tipo de Gênero", generos_disponiveis, default=generos_disponiveis)

# Filtro por Plataforma
plataformas_disponiveis = sorted(df["Plataforma"].unique())
plataformas_selecionadas = st.sidebar.multiselect("Plataforma", plataformas_disponiveis, default=plataformas_disponiveis)

# Filtro de Empresa de Jogos
empresas_disponiveis = sorted(df["Empresa_Jogos"].unique())
empresas_selecionadas = st.sidebar.multiselect("Empresa de Jogos", empresas_disponiveis, default=empresas_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df["Ano"].isin(anos_selecionados)) &
    (df["Gênero"].isin(generos_selecionados)) &
    (df["Plataforma"].isin(plataformas_selecionadas)) &
    (df["Empresa_Jogos"].isin(empresas_selecionadas))
]

# --- Conteúdo Principal ---
st.title("🎮 Dashboard de Análise de Vendas Globais de Jogos de Video-game")
st.markdown("Explore os dados de vendas do top 50 jogos de 1984 a 2015. Use os filtros à esquerda para refinar a sua análise.")
st.markdown("---")


# --- Métricas Principais (KPIs) ---
st.subheader("Métricas Gerais")

# --- Função para formatar a unidade  ---
def formatar_milhoes(valor):
    """
    Formata números para milhões ou bilhões.
    Ex.: 1011.14 -> '1,011 bi'
         350.25  -> '350,250 mi'
    """
    if valor >= 1000:  # 1000 milhões = 1 bilhão
        valor_formatado = valor / 1000
        return f"{valor_formatado:,.3f} bi"
    else:
        return f"{valor:,.3f} mi"

# Calculando as métricas
if not df_filtrado.empty:
    total_vendas_globais = df_filtrado["Vendas_Globais"].sum()
    jogo_mais_vendido = df_filtrado.loc[df_filtrado["Vendas_Globais"].idxmax()]["Nome"]
    genero_mais_frequente = df_filtrado["Gênero"].mode()[0]
    total_registros = len(df_filtrado)
else:
    total_vendas_globais, jogo_mais_vendido, genero_mais_frequente, total_registros = 0, "", "", 0
    st.warning("Nenhum dado encontrado para os filtros selecionados.")

# Cria 4 colunas para as métricas
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de Vendas Globais", f"${formatar_milhoes(total_vendas_globais)}")    
col2.metric("Jogo Mais Vendido", jogo_mais_vendido)
col3.metric("Gênero de Jogo Mais Popular", genero_mais_frequente)
col4.metric("Total de Registros", f"{total_registros}")

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_generos = df_filtrado.groupby('Gênero')['Vendas_Globais'].sum().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_generos = px.bar(
            top_generos,
            x='Vendas_Globais',
            y='Gênero',
            orientation='h',
            title="Top 10 gêneros de jogos mais vendidos globalmente",
            labels={'Vendas_Globais': 'Vendas Globais (milhões)', 'Gênero': ''},
            color_discrete_sequence=PALETA
        )
        grafico_generos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_generos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de gêneros.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='Ano',
            nbins=30,
            title="Distribuição do número de jogos lançados por ano",
            labels={'Ano': 'Anos', 'count': ''},
            color_discrete_sequence=PALETA
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:

        total_na = df_filtrado["Vendas_NA"].sum()
        total_eu = df_filtrado["Vendas_EU"].sum()
        total_jp = df_filtrado["Vendas_JP"].sum()
        total_outros = df_filtrado["Outras_Vendas"].sum()

        df_pizza = pd.DataFrame({
            'Região': ['América do Norte', 'Europa', 'Japão', 'Outras'],
            'Vendas': [total_na, total_eu, total_jp, total_outros]})

        grafico_regiao = px.pie(
            df_pizza,
            names='Região',
            values='Vendas',
            title='Proporção das Vendas de Jogos por Região',
            color_discrete_sequence=PALETA
        )
        grafico_regiao.update_traces(textinfo='percent+label', textfont_size=14)
        grafico_regiao.update_layout(title_x=0.1)
        st.plotly_chart(grafico_regiao, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico das regiões.")

with col_graf4:
    if not df_filtrado.empty:

        # Obter as 3 empresas com maior venda total do DataFrame
        top_empresas_nomes = df_filtrado.groupby('Empresa_Jogos')['Vendas_Globais'].sum().nlargest(3).index.tolist()

        # Filtrar o DataFrame para incluir apenas as principais empresas
        df_top_empresas = df_filtrado[df_filtrado['Empresa_Jogos'].isin(top_empresas_nomes)]

        # Agrupar por ano e empresa e somar as vendas globais
        vendas_por_ano_empresa = df_top_empresas.groupby(['Ano', 'Empresa_Jogos'])['Vendas_Globais'].sum().reset_index()

        grafico_empresas = px.line(
            vendas_por_ano_empresa,
            x='Ano',
            y='Vendas_Globais',
            color='Empresa_Jogos',
            title="Evolução das vendas globais das 3 principais empresas ao longo do tempo",
            color_discrete_sequence=PALETA
        )
        grafico_empresas.update_layout(xaxis_title="Anos", yaxis_title="Vendas Globais (milhões)")
        st.plotly_chart(grafico_empresas, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de empresas.")


# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)