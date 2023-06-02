import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import re
import folium
import numpy as np

import streamlit as st
from streamlit_folium import folium_static

st.set_page_config(page_title='Home Visão', layout='wide', page_icon=':cook:')

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

def time_mean_festival(data, festival):
    columns = ['Time_taken(min)', 'Festival']
    group = ['Festival']
    dt_aux = data[columns].groupby(group).agg({'Time_taken(min)':['mean', 'std']})
    dt_aux.columns = ['time_mean', 'time_std']
    dt_aux = dt_aux.reset_index()

    return dt_aux[dt_aux['Festival'] == festival]

def time_mean_distance(data):
    columns = ['Time_taken(min)', 'City']
    group = ['City']
    dt_aux = data[columns].groupby(group).agg({'Time_taken(min)':['mean', 'std']})
    dt_aux.columns = ['time_mean', 'time_std']
    dt_aux = dt_aux.reset_index()

    fig = go.Figure()
    fig.add_trace( go.Bar(name='Control', x=dt_aux['City'], y=dt_aux['time_mean'], error_y=dict(type='data', array=dt_aux['time_std'])) )

    fig.update_layout(barmode='group')

    return fig

def time_mean_distance_city(data):
    columns = ['Time_taken(min)', 'City', 'Road_traffic_density']
    group = ['City', 'Road_traffic_density']
    dt_aux = data[columns].groupby(group).agg({'Time_taken(min)':['mean', 'std']})
    dt_aux.columns = ['time_mean', 'time_std']
    dt_aux = dt_aux.reset_index()

    return px.sunburst(dt_aux, path=['City', 'Road_traffic_density'], values='time_mean', color='time_std', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(dt_aux['time_std']))

def time_mean_distance_type(data):
    columns = ['Time_taken(min)', 'City', 'Type_of_order']
    group = ['City', 'Type_of_order']
    dt_aux = data[columns].groupby(group).agg({'Time_taken(min)':['mean', 'std']})
    dt_aux.columns = ['time_mean', 'time_std']
    return dt_aux.reset_index()

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
tb1, tb2, tb3 = st.tabs(['Visão Gerencial', '_', '_'])

with tb1:
    with st.container():
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = len(data['Delivery_person_ID'].unique())
            col1.metric('Entregadores', delivery_unique)
        with col2:
            avg_distance = data['km_order'].mean()
            avg_distance = np.round(avg_distance, 2)
            col2.metric('Distancia média', avg_distance)
        with col3:
            dt_aux = time_mean_festival(data, 'Yes')
            col3.metric('T/ Media por festival', np.round(dt_aux['time_mean'], 2))
        with col4:
            dt_aux = time_mean_festival(data, 'Yes')
            col4.metric('D/ Padrão festival', np.round(dt_aux['time_std'], 2))
        with col5:
            dt_aux = time_mean_festival(data, 'No')
            col5.metric('T/ Media por festival', np.round(dt_aux['time_mean'], 2))
        with col6:
            dt_aux = time_mean_festival(data, 'No')
            col6.metric('D/ Padrão festival', np.round(dt_aux['time_std'], 2))
            
    with st.container():
        st.markdown("""---""")
        avg_distance = data[['City', 'km_order']].groupby(['City']).mean().reset_index()
        fig = go.Figure( data=[ go.Pie(labels=avg_distance['City'], values=avg_distance['km_order'], pull=[0,0.1,0]) ] )
        st.plotly_chart(fig)
    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(time_mean_distance(data), use_container_width=True)
        with col2:
            st.plotly_chart(time_mean_distance_city(data), use_container_width=True)

    with st.container():
        st.markdown("""---""")
        st.dataframe(time_mean_distance_type(data), use_container_width=True)
