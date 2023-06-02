from PIL import Image
import streamlit as st

st.set_page_config(
    page_title='Home Visão',
    layout='wide',
    page_icon='house'
)

st.sidebar.markdown("# Cury Company")
st.sidebar.markdown("## Fast Delivery in Town")
st.sidebar.markdown("""---""")

st.write("# Cury Company Growth Dashboard")
st.markdown(
    """
        Growth Dashboard foi construido para acompanhas as métricas de crescimentos dos Restaurantes e Entregadores.
        ### Como ultilizar esse Growth Dashbord?
        - Visão Empresa:
            - Visão Gerencial: Métricas gerais de comportamentos
            - Visão Tática: Indicadores semanais de crescimento
            - Visão Geográfica: Insights de geolocalizão.
        - Visão Entregador:
            - Acompanhamento dos indicadores semanais de crescimento
        - Visão Restaurante:
            - Indicadores semanais de crescimento dos restaurantes
    """
)
