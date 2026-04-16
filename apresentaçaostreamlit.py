import streamlit as st
import time
import pandas as pd
import datetime
import graphviz
import selenium as webdriver
VENDAS30 = pd.read_excel(r"C:\Users\joao.altafini\Downloads\Venda_30,streamlit.xlx.xlsx")

opcao = st.sidebar.selectbox(
    "Escolha uma opção:",
    ["INICIO", "meta venda","Quantidade - Venda","Valor - Venda"]
)
if opcao == "INICIO":
    st.write("Você escolheu:", opcao)
    st.set_page_config("inicio: dados gerais","📈","wide",initial_sidebar_state=400)
    st.title("PAGINA DE APRESENTAÇÃO")
    st.title('Analise geral de dados a abaixo em realação ao vendas 30')
    st.subheader("aolado um ainel com todas as informações do arquivo:")
    st.subheader("vendas 30 visualização logo abaixo")
    st.date_input("coloque sua data aqui embaixo:")
    st.datetime_input("coloque a data via calendario")
    st.selectbox("selecione as opções a seguir",["DATA","N°"])
    st.number_input("digite aqui o numero da loja dos dados separadamenete",min_value=1, max_value=30)
    st.balloons()
    st.subheader("vendas 30 geral")
    st.write(VENDAS30)
    INFOVENDAS30 = VENDAS30.info()
    st.subheader("informações de venda 30")
    st.write(INFOVENDAS30)
    maximovendas30 = VENDAS30.max()
    minvendas30 = VENDAS30.min()
    primeiraslinhasvendas30 = VENDAS30.head(10)
    st.subheader("maior valor de vanda 30")
    st.write(maximovendas30)
    st.subheader("minimode valor de venda 30")
    st.write(minvendas30)
    st.subheader("primeiras linhas de venda 30")
    st.write(primeiraslinhasvendas30)
    contagemderegistros = VENDAS30.count()
    st.subheader("contagem de registros na venda 30")
    st.write(contagemderegistros)
    st.status("dados carregados")
    vendas30media = VENDAS30['Meta_Venda'].mean()
    st.subheader("media de venda 30")
    st.write(vendas30media)
    st.subheader("assinatura: time de io")
elif opcao == "meta venda":
    st.set_page_config("DADOs: meta venda","📈",layout="wide")
    st.title('Analise geral de dados a abaixo em realação ao meta venda')
    st.subheader("aolado um ainel com todas as informações do arquivo:")
    st.subheader("Fluxo de análise das Analise")

    grafico = graphviz.Digraph()

    grafico.node('A', 'Carregar Dados')
    grafico.node('B', 'Analisar Vendas')
    grafico.node('C', 'Calcular Média')
    grafico.node('D', 'Exibir Resultados')

    grafico.edges(['AB', 'BC', 'CD'])
    VENDAS30['Data'] = pd.to_datetime(VENDAS30['DATA'], errors='coerce')

    data_inicio, data_fim = st.date_input(
    "Selecione o período:",
    [VENDAS30['Data'].min(), VENDAS30['Data'].max()],
    key="filtro_data"
    )

    dados_filtrados = VENDAS30[
    (VENDAS30['Data'] >= pd.to_datetime(data_inicio)) &
    (VENDAS30['Data'] <= pd.to_datetime(data_fim))
    ]
    st.graphviz_chart(grafico)


    st.subheader("Meta de Vendas por Loja")

    dados = dados_filtrados.set_index('N°')
    st.bar_chart(dados['Meta_Venda'])
    st.subheader("Meta venda por categoria")
    dados = dados_filtrados.set_index(' CATEGORIA')
    st.bar_chart(dados['Meta_Venda'])
    st.subheader("Média por loja")

    media_cat = dados_filtrados.groupby('N°')['Meta_Venda'].mean()
    st.bar_chart(media_cat)
    st.success("dados carregados")
    #
    st.subheader("Média por categoria")

    media_cat = dados_filtrados.groupby(' CATEGORIA')['Meta_Venda'].mean()
    st.bar_chart(media_cat)
    st.success("dados carregado")
    st.subheader("assinatura: time de io")
elif opcao == "Quantidade - Venda":
    st.set_page_config("DADOS DE QTD DE VENDA","📈",layout="wide")
    st.title('Analise geral de dados a abaixo em realação ao Quantidade - Venda')
    st.subheader("aolado um ainel com todas as informações do arquivo:")
    st.subheader("Fluxo de análise das  Analises")

    grafico = graphviz.Digraph()
    grafico.node('A', 'Carregar Dados')
    grafico.node('B', 'Analisar Vendas')
    grafico.node('C', 'Calcular Média')
    grafico.node('D', 'Exibir Resultados')
    grafico.edges(['AB', 'BC', 'CD'])
    VENDAS30['Data'] = pd.to_datetime(VENDAS30['DATA'], errors='coerce')

    data_inicio, data_fim = st.date_input(
    "Selecione o período:",
    [VENDAS30['Data'].min(), VENDAS30['Data'].max()],
    key="filtro_data"
    )
    st.graphviz_chart(grafico)
    dados_filtrados = VENDAS30[
    (VENDAS30['Data'] >= pd.to_datetime(data_inicio)) &
    (VENDAS30['Data'] <= pd.to_datetime(data_fim))
    ]
    st.graphviz_chart(grafico)

    st.subheader("Quantidade de Vendas por Loja")
    dados = dados_filtrados.set_index('N°')
    st.bar_chart(dados['Quantidade - Venda'])

    st.success("carregado com sucesso")
    st.subheader("Quantidade de Vendas por categoria")
    dados = dados_filtrados.set_index(' CATEGORIA')
    st.bar_chart(dados['Quantidade - Venda'])
    st.subheader("Média por loja")

    media_cat = dados_filtrados.groupby('N°')['Quantidade - Venda'].mean()
    st.bar_chart(media_cat)
    st.success("dados carregados")
    #
    st.subheader("Média por categoria")

    media_cat = dados_filtrados.groupby(' CATEGORIA')['Quantidade - Venda'].mean()
    st.bar_chart(media_cat)
    st.success("dados carregado")
    st.subheader("assinatura: time de io")
elif opcao == "Valor - Venda":
    st.set_page_config("Dados: valor venda","📈",layout="wide")
    st.title('Analise geral de dados a abaixo em realação ao Valor - Venda')
    st.subheader("aolado um ainel com todas as informações do arquivo:")
    st.subheader("Fluxo de análise das Analise")

    grafico = graphviz.Digraph()
    grafico.node('A', 'Carregar Dados')
    grafico.node('B', 'Analisar Vendas')
    grafico.node('C', 'Calcular Média')
    grafico.node('D', 'Exibir Resultados')
    grafico.edges(['AB', 'BC', 'CD'])
    VENDAS30['Data'] = pd.to_datetime(VENDAS30['DATA'], errors='coerce')

    data_inicio, data_fim = st.date_input(
    "Selecione o período:",
    [VENDAS30['Data'].min(), VENDAS30['Data'].max()],
    key="filtro_data"
    )
    st.graphviz_chart(grafico)
    dados_filtrados = VENDAS30[
    (VENDAS30['Data'] >= pd.to_datetime(data_inicio)) &
    (VENDAS30['Data'] <= pd.to_datetime(data_fim))
    ]
    st.graphviz_chart(grafico)

    st.subheader("Valor - Venda por Loja")
    dados = dados_filtrados.set_index('N°')
    st.bar_chart(dados['Valor - Venda'])

    st.success("carregado com sucesso")
    st.subheader("Valor - Venda por categoria")
    dados = dados_filtrados.set_index(' CATEGORIA')
    st.bar_chart(dados['Valor - Venda'])
    st.success("dados carregados")
    st.subheader("Média por loja")

    media_cat = dados_filtrados.groupby('N°')['Valor - Venda'].mean()
    st.bar_chart(media_cat)
    st.success("dados carregados")
    #
    st.subheader("Média por categoria")

    media_cat = dados_filtrados.groupby(' CATEGORIA')['Valor - Venda'].mean()
    st.bar_chart(media_cat)
    st.success("dados carregado")
    st.subheader("assinatura: Time de io")


