import pandas as pd
import plotly.express as px
import re
import folium
from haversine import haversine

import streamlit as st
from streamlit_folium import folium_static

st.set_page_config(page_title='Home Visão', layout='wide', page_icon=':bar_chart')

# -------------------
# FUNÇÕES
# -------------------
def clean_code(data):
    """ Esta função tem a responsabilidade de limpar o dataframe

        Tipos de limpeza:
        1. Tirando valores NaN
        2. Arrumando os tipos de colunas conforme seu dado
        3. Tirando espaços dos valores nos ultimo caracter
        4. Tirando caractares não numericos da coluna Time_taken(min)
        5. Formatando para campo datas os valores
        6. Criando campo numero da semana
        7. Criando campo de distancia do restaurante até a entrega

        Input: DataFrame
        Output: DataFrame

    """

    # Tirando valores NaN e arrumando a coluna para INT na Delivery_person_Age
    data = data[data['Delivery_person_Age'] != 'NaN ']
    data['Delivery_person_Age'] = data['Delivery_person_Age'].astype(int)

    # Tirando valores NaN e tirando espaços da City
    data = data[data['City'] != 'NaN ']
    data['City'] = data['City'].str.strip()

    # Order_Date colocando como uma coluna datatime
    data['Order_Date'] = pd.to_datetime(data['Order_Date'], dayfirst=True)

    # Delivery_person_Ratings tirando o NaN e colocando coluna como float
    data = data[data['Delivery_person_Ratings'] != 'NaN ']
    data = data[data['Delivery_person_Ratings'].notnull()]
    data['Delivery_person_Ratings'] = data['Delivery_person_Ratings'].astype(float)

    # Tirando espace da coluna Delivery_person_ID
    data['Delivery_person_ID'] = data['Delivery_person_ID'].str.strip()

    # Tirando os "conditions NaN" da coluna Weatherconditions
    data = data[data['Weatherconditions'] != 'conditions NaN']

    # Road_traffic_density tirando espaços
    data['Road_traffic_density'] = data['Road_traffic_density'].str.strip()

    # Type_of_order tirando espaços
    data['Type_of_order'] = data['Type_of_order'].str.strip()

    # Type_of_vehicle tirando espaços
    data['Type_of_vehicle'] = data['Type_of_vehicle'].str.strip()

    # Festival tirando espaços e NaN
    data['Festival'] = data['Festival'].str.strip()
    data = data[data['Festival'] != 'NaN']

    # Arrumando os valores de Time_taken(min)
    data['Time_taken(min)'] = data['Time_taken(min)'].apply(lambda x: re.sub(r"\D", "", x))
    data['Time_taken(min)'] = data['Time_taken(min)'].astype(int)

    # (Criamos um campo para o numero da semana)
    data['order_week'] = data['Order_Date'].dt.strftime('%U')

    # Criando KM do restaurante para entrega
    data['km_order'] = ( data.apply(lambda x: haversine(
                                            (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1) )

    return data

def day_order(data):
    columns = ['ID', 'Order_Date']
    group = ['Order_Date']
    order_per_day = data[columns].groupby(group).count().reset_index()
    return px.bar(order_per_day, x='Order_Date', y='ID')

def traffic_order_share(data):
    columns = ['ID', 'Road_traffic_density']
    group = ['Road_traffic_density']
    df_aux = data[columns].groupby(group).count().reset_index()
    df_aux['entrega_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    return px.pie(df_aux, values='entrega_perc', names='Road_traffic_density')

def traffic_order_city(data):
    df_aux = data.loc[(data['City'] != "NaN ") & (data['Road_traffic_density'] != "NaN "), ['ID', 'Road_traffic_density', 'City']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    return px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color="City")

def week_order(data):
    df_aux_order = data.loc[:, ['ID', 'order_week']].groupby(['order_week']).count().reset_index()
    return px.line(df_aux_order, x='order_week', y='ID')

def delivery_orders(data):
    df_aux_order = data.loc[:, ['ID', 'order_week']].groupby(['order_week']).count().reset_index()
    df_aux_person = data.loc[:, ['order_week', 'Delivery_person_ID']].groupby(['order_week']).nunique().reset_index()
    df_aux = df_aux_order.merge(df_aux_person, how='inner')
    df_aux['per_order_person'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    return px.line(df_aux, x='order_week', y='per_order_person')

def country_maps(data):
    df_aux = data.loc[:, ['City', 'Delivery_location_longitude', 'Delivery_location_latitude', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    map = folium.Map()

    for index, location in df_aux.iterrows():
        folium.Marker([
            location['Delivery_location_latitude'],
            location['Delivery_location_longitude']
        ]).add_to(map)

    # map
    folium_static(map, width=1024, height=600)

# ----------------------------------------- Start Logíca ----------------------------------------- #
# ---------------------
# Import dataset
# ---------------------
data = pd.read_csv('datasets/train.csv')

# ---------------------
# Limpando dados
# ---------------------
data = clean_code(data)


# ################## VISÃO Negocio ################## #

# ------------> BARRA LATERAL SIDEBAR


# ------------> BARRA LATERAL SIDEBAR
dt_min = pd.Timestamp(data['Order_Date'].min())
dt_max = pd.Timestamp(data['Order_Date'].max())
dt_min = dt_min.to_pydatetime()
dt_max = dt_max.to_pydatetime()

st.header('Marketplace - Visão entregadores')

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

# --------------
# STREAMLIT - Filtrar por data
# --------------
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=dt_max,
    min_value=dt_min,
    max_value=dt_max,
    format='DD-MM-YYYY'
)

# --------------
# STREAMLIT - Filtrar por codições de trânsito
# --------------
traffic_option = st.sidebar.multiselect('Quais as condições de trânsito?', data['Road_traffic_density'].unique(), default=data['Road_traffic_density'].unique())
st.sidebar.markdown("""---""")
st.sidebar.markdown("### Powered by Fernando Batista")

# Filtro de datas
linhas_selecionadas = data['Order_Date'] <= date_slider
data = data.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = data['Road_traffic_density'].isin(traffic_option)
data = data.loc[linhas_selecionadas, :]

# --------------
# STREAMLIT - LAYOUT CONTAINER
# --------------
tb1, tb2, tb3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tb1:
    with st.container():
        # Quantidade de pedidos por dia
        st.markdown("# Orders by day")
        st.plotly_chart(day_order(data), use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            st.plotly_chart(traffic_order_share(data), use_container_width=True)
        with col2:
            st.header('Traffic Order City')
            st.plotly_chart(traffic_order_city(data), use_container_width=True)

with tb2:
    with st.container():
        st.markdown("# Order Per Week")
        #Pedidos por semana
        st.plotly_chart(week_order(data), user_container_width=True)

    with st.container():
        st.markdown("# Order Share by Week")
        #Pedidos por entregadores
        st.plotly_chart(delivery_orders(data), user_container_width=True)

with tb3:
    st.markdown("# Country Maps")
    country_maps(data)
