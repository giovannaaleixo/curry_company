#==============================================================
# BIBLIOTECAS
#=============================================================
import pandas as pd
#Importando bibliotecas necessárias para criar Dashboard
import streamlit as st
from PIL import Image
import plotly.express as ex
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='', layout='wide')

#=====================================================
# FUNÇÕES
#=====================================================

def clean_code (df1):
    """ Essa função tem como objetivo a limpeza e preparação do dataframe
            Tipos de limpeza:
            1. Remover os dados NaN 
            2. Alterar o tipo da coluna de dados
            3. Remoção dos espaços das variáveis de texto
            4. Formatação da coluna de datas
            5. Limpeza da coluna de tempo 
            
            Input: Dataframe
            Output: Dataframe       
    """
    
    # 1. Converter a coluna Delivery_person_Age para formato int.
    linha_idade = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linha_idade, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    # 2. Converter a coluna Delivery_person_Ratings para float.
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    # 3. Converter a coluna Order_Date para data.
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')

    # 4. Converter coluna multiple_deliveries para formato int.
    linhas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    #Remover NaN
    linha_idade = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linha_idade, :].copy()

    # Limpando a coluna Time_taken:
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    # 5. Remover os espaços dos textos/string/objects
        #alternativa ao FOR
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip() 
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip() 
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip() 
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip() 
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    
    return df1

def top_delivers(df1, top_asc):
    df2 = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City','Delivery_person_ID']).max().sort_values(['City', 'Time_taken(min)'], ascending = top_asc).reset_index()

    df_aux1 = df2.loc[df2['City'] == 'Metropolitian'].head(10)
    df_aux2 = df2.loc[df2['City'] == 'Urban'].head(10)
    df_aux3 = df2.loc[df2['City'] == 'Semi-Urban'].head(10)
    entregadores_10 = pd.concat([df_aux1 ,df_aux2, df_aux3]).reset_index(drop=True)
                
    return entregadores_10



#------------------------------------------------------------------------------------------------------------------
# ---------------------------------------Inicio Estrutura lógica do código ----------------------------------------

# Lendo dataset
df = pd.read_csv('dataset/train.csv')

# Limpando o dataset
df1 = clean_code(df)

# ==============================================
# Barra lateral do Dashboard
# ==============================================
st.header('Marketplace - Visão Entregadores')
image_path = 'food_delivery.jpg'
image = Image.open(image_path)
st.sidebar.image(image, width = 300)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual valor?', value=pd.datetime(2022, 4, 13), min_value=pd.datetime(2022,2,11),max_value=pd.datetime(2022,4,6), format='DD/MM/YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect('Quais as condições do trânsito', ['Low', 'Medium', 'High', 'Jam'],default='Low')

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS - Giovanna Aleixo')

#Filtro para a Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro para o tipo de Trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# ==============================
# Layout no Streamlit
# =============================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    
    with st.container():
        
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap ='large')
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
            
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            melhor_veiculo = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição', melhor_veiculo)             
            
        with col4:
            pior_veiculo = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição', pior_veiculo)
        
    with st.container():
        
        st.markdown("""---""")
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('Avaliações média por entregador')
            df_ratings_per_deliver = df1.loc[:, ['Delivery_person_ID','Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(df_ratings_per_deliver)
            
        with col2:
            st.subheader('Avaliação média por trânsito')
            
            df_ratings_per_traffic = df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean','std']})
            #agg função de agregação
            df_ratings_per_traffic.columns = ['deliver_mean', 'deliver_std'] #renomear colunas
            df_ratings_per_traffic = df_ratings_per_traffic.reset_index() #resetar index das linhas
            st.dataframe(df_ratings_per_traffic)
      
    
            st.subheader('Avaliação média por clima')
            df_ratings_weather = df1.loc[:,['Delivery_person_Ratings','Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings': ['mean', 'std']})
            df_ratings_weather.columns = ['Ratings_mean', 'Ratings_std']
            df_ratings_weather = df_ratings_weather.reset_index()
            st.dataframe(df_ratings_weather)
        
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader('Entregadores mais rápidos')
            entregadores_10 = top_delivers(df1, top_asc=True)
            st.dataframe(entregadores_10)
        
        with col2:
            st.subheader('Entregadores mais lentos')
            entregadores_10 = top_delivers(df1, top_asc=False)
            st.dataframe(entregadores_10)