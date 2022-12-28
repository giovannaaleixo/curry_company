# Primeiro Passo: Enviar o dataset para a nuvem via comando e importar os dados através da biblioteca Pandas.
import pandas as pd

#Importando bibliotecas necessárias
import streamlit as st
from PIL import Image
import plotly.express as ex
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon='', layout='wide')

#==================================================
# FUNÇÕES
#==================================================

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

def order_metric(df1):
    # Seleção de colunas
    col1 = ['ID', 'Order_Date']

    # Agrupamento
    df_aux = df1.loc[:, col1].groupby('Order_Date').count().reset_index() #importante resetar o index para criar os gráficos
            
    # Criar gráfico de barras
    fig = ex.bar(df_aux, x = 'Order_Date', y = 'ID')
            
    return fig

def traffic_order_share(df1):
    # Agrupamento
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()

    # Remover o dado NaN dos dados da coluna Road_traffic_density
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

    # Calcular percentual de entregas por cada tipo de trafego
    df_aux['percentil_entregas'] = df_aux['ID'] / df_aux['ID'].sum()

    # Criando um gráfico de pizza
    fig = ex.pie(df_aux, values='percentil_entregas', names='Road_traffic_density')
                
    return fig


def traffic_order_city(df1):
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    #df_aux = df1.loc[:, ['ID', 'City', 'Type_of_vehicle']].groupby(['City', 'Type_of_vehicle']).count().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :] #Remover NaN da coluna
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

    # Criar gráfico de bolhas
    fig = ex.scatter(df_aux, x='City', y='Road_traffic_density', size = 'ID', color = 'City')
                
    return fig

def order_by_week(df1):
    
    # Criar uma nova coluna - semanas do ano
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    # Selecionar colunas
    col = ['ID', 'week_of_year']

    # Agrupamento
    df_aux = df1.loc[:, col].groupby('week_of_year').count().reset_index()

    # Criar o gráfico de linhas
    fig = ex.line(df_aux, x = 'week_of_year', y = 'ID')
            
    return fig

def order_share_by_week(df1):
                
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

    # Unir DataFrames
    df_aux = pd.merge(df_aux01, df_aux02, how='inner') 

    # Divisão
    df_aux['Order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    # Criar o gráfico de linhas
    fig = ex.line(df_aux, x = 'week_of_year', y= 'Order_by_deliver')
            
    return fig


def country_maps(df1):
    # Agrupamento
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    # Remover NaN
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]

    # Criar um mapa
    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], 
                         location_info['Delivery_location_longitude']]).add_to(map)

    #Exibir o mapa no Streamlit
    folium_static(map, width=1024, height=600)
        
    return None

#============================== Início da estrutura lógica do código ===================
#----------------------------------
# Importando os dados
#----------------------------------
df = pd.read_csv('dataset/train.csv')

#----------------------------------
# Limpando os dados
#----------------------------------
df1 = clean_code(df)


# ==============================
# Barra lateral
# =============================
st.header('Marketplace - Visão Empresa')
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

#Criar abas 
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #Order Metric    
        st.markdown('# Orders by Day')
        fig = order_metric(df1) 
        st.plotly_chart(fig, use_container_width=True)
                
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1: 
            st.header('Traffic Order Share')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)
                       
        with col2: 
            st.header('Traffic Order City')
            fig = traffic_order_city(df1) 
            st.plotly_chart(fig, use_container_width=True)                 

            
with tab2:
    with st.container():
        st.markdown('# Orders by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)
              
    with st.container():
        # Quantidade de pedidos por semana / Número único de entregadores por semana.
        st.markdown('# Orders by Share by Week')
        fig = order_share_by_week(df1)
        st.plotly_chart(fig, use_container_width=True)      
    

with tab3:
    st.markdown('# Country Maps')
    country_maps(df1)