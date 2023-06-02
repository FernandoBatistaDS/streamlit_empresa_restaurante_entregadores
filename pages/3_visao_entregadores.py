import pandas as pd
import re
from haversine import haversine

import streamlit as st

st.set_page_config(page_title='Home Visão', layout='wide', page_icon=':truck')


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

    """ Esta função tem a responsabilidade de limpar o dataframe

        Tipos de limpeza:
        1. Tirando valores NaN
        2. Arrumando os tipos de colunas conforme seu dado
        3. Tirando espaços dos valores nos ultimo caracter
        4. Tirando caractares não numericos da coluna Time_taken(min)
        5. Formatando para campo datas os valores

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

    return data

def delivery_ratings(data, field):
    df_aux = data.loc[:, ['Delivery_person_Ratings', field]].groupby([field]).agg({'Delivery_person_Ratings': ['mean', 'std']})
    df_aux.columns = ['delivery_mean', 'delivery_std']
    return df_aux.reset_index()

def top_delivers(data, order):
    dt_aux = data.loc[:, ['City', 'Time_taken(min)', 'Delivery_person_ID']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['City', 'Time_taken(min)'], ascending=order).reset_index()

    dt_aux1 = dt_aux[dt_aux['City'] == 'Metropolitian'].head(10)
    dt_aux2 = dt_aux[dt_aux['City'] == 'Urban'].head(10)
    dt_aux3 = dt_aux[dt_aux['City'] == 'Semi-Urban'].head(10)

    return pd.concat([dt_aux1, dt_aux2, dt_aux3]).reset_index(drop=True)


# ----------------------------------------- Start Logíca ----------------------------------------- #
# ---------------------
# Import dataset
# ---------------------
data = pd.read_csv('datasets/train.csv')

# ---------------------
# Limpando dados
# ---------------------
data = clean_code(data)



# ################## VISÃO ENTREGADORES ################## #

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
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # st.subheader('Maior idade')
            col1.metric('Maior idade', data['Delivery_person_Age'].max())
        with col2:
            # st.subheader('Menor idade')
            col2.metric('Menor idade', data['Delivery_person_Age'].min())
        with col3:
            # st.subheader('Melhor condição de veiculos')
            col3.metric('Melhor cond veículo', data['Vehicle_condition'].max())
        with col4:
            # st.subheader('Pior condição de veiculos')
            col4.metric('Melhor cond veículo', data['Vehicle_condition'].min())
    with st.container():
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação medias por entregador')
            df_aux = data[['Delivery_person_Ratings', 'Delivery_person_ID']].groupby(['Delivery_person_ID']).mean().reset_index()
            st.dataframe(df_aux)
        with col2:
            st.markdown('##### Avaliação medias por trânsito')
            st.dataframe(delivery_ratings(data, 'Road_traffic_density'))

            st.markdown('##### Avaliação medias por clima')
            st.dataframe(delivery_ratings(data, 'Weatherconditions'))

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade por Entrega')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top entregadores mais rapidos')
            st.dataframe(top_delivers(data, True))
        with col2:
            st.markdown('##### Top entregadores mais lendos')
            st.dataframe(top_delivers(data, False))
with tb2:
    st.markdown("# Tab 2")
with tb3:
    st.markdown("# Tab 3")





