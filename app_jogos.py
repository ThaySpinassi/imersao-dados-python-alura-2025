import streamlit as st                     # biblioteca para criar o dashboard web
import pandas as pd                        # biblioteca para manipular dados (DataFrame/CSV)
import plotly.express as px                # biblioteca para criar gráficos interativos

# --- Configuração da Página ---
# Define título da aba, ícone e modo de largura total da página.
st.set_page_config(
    page_title="Dashboard de Vendas de Jogos",  # texto que aparece na aba do navegador
    page_icon="🎮",                              # emoji/ícone da aba
    layout="wide",                               # usa a largura inteira da tela
)

# --- Paleta global ---
PALETA = px.colors.qualitative.D3               # paleta de cores discreta (categorias) usada nos gráficos

# --- Carregamento dos dados ---
try:
    df = pd.read_csv("top_50_jogos.csv")        # tenta ler o CSV 
except FileNotFoundError:
    st.error("Erro: O arquivo 'top_50_jogos.csv' não foi encontrado. Verifique o caminho.")  # mostra erro amigável
    st.stop()                                   # interrompe a execução do app para evitar falhas adiante

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros")                 # título da seção de filtros na sidebar

# Filtro de Ano
anos_disponiveis = sorted(df["Ano"].unique(), reverse=True)                 # lista de anos únicos, ordenados do mais recente
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis,         # multiselect permite escolher um ou vários anos
                                           default=anos_disponiveis)        # por padrão, todos os anos já vêm selecionados

# Filtro por Tipo de Gênero
generos_disponiveis = sorted(df["Gênero"].unique())                         # lista de gêneros únicos, ordenados A→Z
generos_selecionados = st.sidebar.multiselect("Tipo de Gênero",             # multiselect para gêneros
                                              generos_disponiveis,
                                              default=generos_disponiveis)  # padrão: todos selecionados

# Filtro por Plataforma
plataformas_disponiveis = sorted(df["Plataforma"].unique())                 # lista de plataformas únicas
plataformas_selecionadas = st.sidebar.multiselect("Plataforma",             # multiselect para plataformas
                                                  plataformas_disponiveis,
                                                  default=plataformas_disponiveis)

# Filtro de Empresa de Jogos
empresas_disponiveis = sorted(df["Empresa_Jogos"].unique())                 # lista de empresas únicas
empresas_selecionadas = st.sidebar.multiselect("Empresa de Jogos",          # multiselect para empresas
                                               empresas_disponiveis,
                                               default=empresas_disponiveis)

# --- Filtragem do DataFrame ---
# Aplica todos os filtros de uma vez; .isin verifica se o valor está entre os selecionados.
df_filtrado = df[
    (df["Ano"].isin(anos_selecionados)) &
    (df["Gênero"].isin(generos_selecionados)) &
    (df["Plataforma"].isin(plataformas_selecionadas)) &
    (df["Empresa_Jogos"].isin(empresas_selecionadas))
]

# --- Conteúdo Principal ---
st.title("🎮 Dashboard de Análise de Vendas Globais de Jogos de Video-game")  # título principal da página
st.markdown("Explore os dados de vendas do top 50 jogos de 1984 a 2015. Use os filtros à esquerda para refinar a sua análise.")  # subtítulo/descrição
st.markdown("---")                                                           # linha horizontal para separar as seções

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas Gerais")                                              # subtítulo da seção de KPIs

# --- Função para formatar a unidade  ---
def formatar_milhoes(valor):
    if valor >= 1000:                         # se for 1000 milhões ou mais (>= 1 bilhão)
        valor_formatado = valor / 1000        # converte milhões para bilhões
        return f"{valor_formatado:,.3f} bi"   # formata com 3 casas
    else:
        return f"{valor:,.3f} mi"             # caso contrário, mantém em milhões com 3 casas

# Calculando as métricas
if not df_filtrado.empty:                                                         # se o DataFrame filtrado tiver dados
    total_vendas_globais = df_filtrado["Vendas_Globais"].sum()                    # soma total das vendas globais (em milhões)
    jogo_mais_vendido = df_filtrado.loc[df_filtrado["Vendas_Globais"].idxmax()]["Nome"]  # pega o "Nome" do jogo com maior venda
    genero_mais_frequente = df_filtrado["Gênero"].mode()[0]                       # gênero que mais aparece (moda)
    total_registros = len(df_filtrado)                                            # quantidade de linhas após filtro
else:
    total_vendas_globais, jogo_mais_vendido, genero_mais_frequente, total_registros = 0, "", "", 0  # valores padrão se vazio
    st.warning("Nenhum dado encontrado para os filtros selecionados.")            # alerta visual na tela

# Cria 4 colunas para as métricas (ficam lado a lado)
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de Vendas Globais", f"${formatar_milhoes(total_vendas_globais)}")  # KPI 1: total de vendas (mostra $ + mi/bi)
col2.metric("Jogo Mais Vendido", jogo_mais_vendido)                                   # KPI 2: nome do jogo com maior venda
col3.metric("Gênero de Jogo Mais Popular", genero_mais_frequente)                     # KPI 3: gênero mais frequente nos dados filtrados
col4.metric("Total de Registros", f"{total_registros}")                               # KPI 4: número de registros após filtrar

st.markdown("---")                                                                    # separador visual

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")                                                              # subtítulo dos gráficos

# Cria uma grade com duas colunas para os dois primeiros gráficos
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        # Agrupa por gênero, soma vendas globais, pega top 10, ordena do menor para o maior (para barra horizontal ficar "crescente")
        top_generos = (
            df_filtrado.groupby('Gênero')['Vendas_Globais'].sum()
            .nlargest(10)                              # pega os 10 maiores totais
            .sort_values(ascending=True)               # ordena para exibir do menor para o maior no eixo Y
            .reset_index()                             # volta a ser DataFrame com coluna 'Gênero'
        )
        # Cria gráfico de barras horizontal (orientation='h')
        grafico_generos = px.bar(
            top_generos,
            x='Vendas_Globais',                        # valor no eixo X (quantidade)
            y='Gênero',                                # categorias no eixo Y (gêneros)
            orientation='h',                           # barras na horizontal
            title="Top 10 gêneros de jogos mais vendidos globalmente",
            labels={'Vendas_Globais': 'Vendas Globais (milhões)', 'Gênero': ''},  # rótulos dos eixos
            color_discrete_sequence=PALETA             # paleta de cores definida no topo
        )
        grafico_generos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})  # posiciona título e ordena categorias
        st.plotly_chart(grafico_generos, use_container_width=True)               # renderiza o gráfico ocupando a largura da coluna
    else:
        st.warning("Nenhum dado para exibir no gráfico de gêneros.")             # aviso se não houver dados filtrados

with col_graf2:
    if not df_filtrado.empty:
        # Histograma: mostra quantos jogos por ano (contagem de linhas em cada ano)
        grafico_hist = px.histogram(
            df_filtrado,
            x='Ano',                                     # eixo X: ano de lançamento
            nbins=30,                                    # quantidade de "caixas" (bins) do histograma
            title="Distribuição do número de jogos lançados por ano",
            labels={'Ano': 'Anos', 'count': ''},         # rótulos dos eixos
            color_discrete_sequence=PALETA               # paleta de cores
        )
        grafico_hist.update_layout(title_x=0.1)          # desloca um pouco o título para a esquerda
        st.plotly_chart(grafico_hist, use_container_width=True)  # mostra o gráfico
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")         # aviso se não houver dados filtrados

# Segunda linha de gráficos (2 colunas)
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:

        # Soma as vendas por região usando apenas os dados filtrados
        total_na = df_filtrado["Vendas_NA"].sum()        # América do Norte
        total_eu = df_filtrado["Vendas_EU"].sum()        # Europa
        total_jp = df_filtrado["Vendas_JP"].sum()        # Japão
        total_outros = df_filtrado["Outras_Vendas"].sum()# Outras regiões

        # Monta um DataFrame simples para alimentar o gráfico de pizza
        df_pizza = pd.DataFrame({
            'Região': ['América do Norte', 'Europa', 'Japão', 'Outras'],
            'Vendas': [total_na, total_eu, total_jp, total_outros]
        })

        # Gráfico de pizza mostrando a proporção de vendas por região
        grafico_regiao = px.pie(
            df_pizza,
            names='Região',                               # fatias nomeadas por região
            values='Vendas',                              # tamanho da fatia = valor de vendas
            title='Proporção das Vendas de Jogos por Região',
            color_discrete_sequence=PALETA                # paleta de cores
        )
        grafico_regiao.update_traces(textinfo='percent+label', textfont_size=14)  # mostra porcentagem e rótulo na fatia
        grafico_regiao.update_layout(title_x=0.1)         # posiciona o título
        st.plotly_chart(grafico_regiao, use_container_width=True)  # exibe o gráfico
    else:
        st.warning("Nenhum dado para exibir no gráfico das regiões.")             # aviso se não houver dados filtrados

with col_graf4:
    if not df_filtrado.empty:

        # Descobre as 3 empresas com maior soma de vendas no recorte filtrado
        top_empresas_nomes = (
            df_filtrado.groupby('Empresa_Jogos')['Vendas_Globais'].sum()
            .nlargest(3)                                  # pega as 3 maiores somas
            .index.tolist()                               # extrai só os nomes (índice → lista)
        )

        # Filtra o DF para conter apenas essas empresas top 3
        df_top_empresas = df_filtrado[df_filtrado['Empresa_Jogos'].isin(top_empresas_nomes)]

        # Soma as vendas por ano para cada empresa (prepara dados para o gráfico de linha)
        vendas_por_ano_empresa = (
            df_top_empresas.groupby(['Ano', 'Empresa_Jogos'])['Vendas_Globais']
            .sum()
            .reset_index()
        )

        # Gráfico de linhas mostrando a evolução anual das vendas das 3 empresas
        grafico_empresas = px.line(
            vendas_por_ano_empresa,
            x='Ano',                                       # eixo X: ano
            y='Vendas_Globais',                            # eixo Y: vendas globais (milhões)
            color='Empresa_Jogos',                         # uma linha por empresa
            title="Evolução das vendas globais das 3 principais empresas ao longo do tempo",
            color_discrete_sequence=PALETA                 # paleta de cores
        )
        grafico_empresas.update_layout(xaxis_title="Anos", yaxis_title="Vendas Globais (milhões)")  # rótulos dos eixos
        st.plotly_chart(grafico_empresas, use_container_width=True)  # exibe o gráfico
    else:
        st.warning("Nenhum dado para exibir no gráfico de empresas.")              # aviso se não houver dados filtrados

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")                     # subtítulo da tabela
st.dataframe(df_filtrado)                            # mostra o DataFrame filtrado em formato de tabela interativa
