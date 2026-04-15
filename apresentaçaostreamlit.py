import streamlit as st
import time
import pandas as pd
import datetime
import graphviz
import selenium as webdriver
VENDAS30 = pd.read_excel(r"C:\Users\joao.altafini\Downloads\Venda_30,streamlit.xlx.xlsx")
opcao = st.sidebar.selectbox(
    "Escolha uma opção:",
    ["INICIO", "VENDAS 30"]
)

st.write("Você escolheu:", opcao)
st.set_page_config("inicio:Boa","📈","wide",initial_sidebar_state=400)
st.title("PAGINA DE APRESENTAÇÃO")
st.subheader("vendas 30 visualização logo abaixo")
st.date_input("coloque sua data aqui embaixo:")
st.datetime_input("coloque a data via calendario")
st.selectbox("selecione as opções a seguir",["DATA","N°"])
st.number_input("digite aqui o numero da loja dos dados separadamenete",min_value=1, max_value=30)
st.balloons()
st.subheader("vendas 30 ")
st.write(VENDAS30)
INFOVENDAS30 = VENDAS30.info()
st.subheader("informações do venda 30")
st.write(INFOVENDAS30)
maximovendas30 = VENDAS30.max()
minvendas30 = VENDAS30.min()
primeiraslinhasvendas30 = VENDAS30.head(10)
st.subheader("maior valor do vanda 30")
st.write(maximovendas30)
st.subheader("minimode valor do venda 30")
st.write(minvendas30)
st.subheader("primeiras linhas do venda 30")
st.write(primeiraslinhasvendas30)
contagemderegistros = VENDAS30.count()
st.subheader("contagem de registros no venda 30")
st.write(contagemderegistros)
st.status("dados carregados")
vendas30media = VENDAS30['Meta_Venda'].mean()
st.subheader("media de venda 30")
st.write(vendas30media)
media = VENDAS30['Meta_Venda'].mean()
soma = VENDAS30['Meta_Venda'].sum()
porcentual = media / soma
st.subheader("abaixo mostraremos em porcentual")
st.write(f"{porcentual:.2%}")
st.success("carregado com sucesso")



