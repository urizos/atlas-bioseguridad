import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from PIL import Image
import webbrowser
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import gcsfs
import urllib.request
from PIL import Image

path = "resoluciones_db_geo_29062020.csv"

# Leyendo datos de resoluciones

data_gmo = pd.read_csv(path, encoding ="latin-1")

# Cargando imágenes

url_legend = 'legend_atlas.png'
url_logo = 'logo_cibiogem.png'
legend = Image.open(urllib.request.urlopen(url_legend))
logo = Image.open(urllib.request.urlopen(url_logo))

# Transform color maps
COLORS_R = {"Algodón": 190, "Maíz": 236, "Soya":153, "Alfalfa":101, "Trigo":135, "Limón mexicano":102, "Frijol":59, "Naranja dulce Valencia":255}

COLORS_G = {"Algodón": 169, "Maíz": 228, "Soya":185, "Alfalfa":74, "Trigo":138, "Limón mexicano":146, "Frijol":185, "Naranja dulce Valencia":181}

COLORS_B = {"Algodón": 146, "Maíz": 86, "Soya":152, "Alfalfa":140, "Trigo":143, "Limón mexicano":61, "Frijol":216, "Naranja dulce Valencia":102}

data_gmo["color_r"] = data_gmo["specie"].map(COLORS_R)
data_gmo["color_g"] = data_gmo["specie"].map(COLORS_G)
data_gmo["color_b"] = data_gmo["specie"].map(COLORS_B)

st.image(logo,use_column_width=True)
st.markdown('''# *Atlas Interactivo de Bioseguridad de los Organismos Genéticamente Modificados*
La Secretaría Ejecutiva de la CIBIOGEM, desarrolla y actualiza el Sistema Nacional de Información sobre Bioseguridad (SNIB)y el Registro Nacional de Bioseguridad de los OGMS (RNB), ambas plataformas están dedicadas a reunir y sintetizar documentos y bases de datos relevantes en materia de bioseguridad y uso y liberación al ambiente de Organismos Genéticamente Modificados. El presente Atlas interactivo de Bioseguridad muestra la información geográfica y estadística de todos los permisos de liberación al ambiente con resolución favorable entre los años 2005 y 2018.''')

# Selectores de información

st.sidebar.subheader('Parámetros de búsqueda')

st.sidebar.markdown('''Empleando los siguientes controles usted podrá filtrar y seleccionar todas las solicitudes de liberación al ambiente de OGM que figuran en el Sistema Nacional de Información en Bioseguridad desde 2005 a 2018. Cada solicitud puede ser selecionada por ```Tipo``` de liberación, ```Año``` de la solicitud y ```Organismo``` de la solicitud.''')

year_to_filter = st.sidebar.slider('Año de solicitud',2005,2018,2005)

type_filter = st.sidebar.selectbox('Tipo de liberación',('Experimental','Programa Piloto', 'Comercial'))

specie_filter = st.sidebar.multiselect('Organismo de la solicitud', list(data_gmo['specie'].unique()),default=['Algodón','Maíz','Soya'])

filtered_data = data_gmo[data_gmo['year'] == year_to_filter]
filtered_data = filtered_data[filtered_data['type'] == type_filter]
filtered_data= filtered_data[filtered_data.specie.isin(specie_filter)]

#Base de datos para el mapa
counter_data = filtered_data.groupby(['cvgeo']).count()[['id']].reset_index()

counter_data = pd.merge(counter_data, filtered_data[['cvgeo','mun','ent','specie','ORGANISMO','FECHA_RESOLUCION','type','lat','lon','color_r','color_g','color_b']], left_on='cvgeo', right_on='cvgeo', how='left')

counter_data = counter_data.drop_duplicates(subset=['cvgeo','specie']).reset_index(drop=True)

if not counter_data.size:
    st.subheader('Esto es embarazoso, intenta otros parámetros')
else:
    table_data = counter_data[['id','mun','ent','specie','ORGANISMO','type','FECHA_RESOLUCION']]
    table_data.columns = ['Número de solicitudes','Municipio','Entidad','Especie','Nombre científico','Tipo de solicitud','Fecha de resolución']

    st.write('## Se muestran todas las solicitudes de tipo', type_filter, 'del año', year_to_filter, 'agrupadas por municipio:')

    st.markdown('**Tabla de Resoluciones**')
    st.write(table_data)

    st.markdown('**Ubicación geográfica de las solicitudes de liberación al ambiente**')
    st.image(legend,use_column_width=True)
    st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=23,
        longitude=-102,
        zoom=4,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            counter_data,
            pickable=True,
            opacity=0.6,
            stroked=True,
            filled=True,
            radius_scale=6,
            radius_min_pixels=1,
            radius_max_pixels=100,
            line_width_min_pixels=1,
            get_position=['lon', 'lat'],
            get_radius="id*2000",
            get_fill_color=['color_r', 'color_g', 'color_b'],
            get_line_color=[0, 0, 0],
        ),
     ],
     tooltip={
        "html": "<b>Organismo:</b> {specie}"
        "<br/> <b>Tipo de liberación:</b> {type}"
        "<br/> <b>Número de solicitudes:</b> {id} "
        "<br/> <b>Municipio de liberación:</b> {mun}"
        "<br/> <b>Estado:</b> {ent}",
        "style": {"color": "white"},
     },
     ))

# Gráfico por estados
    try: 
        colorsIdx = {'Algodón': '#bea992', 'Maíz': '#ece556','Soya':"#99b998", 'Alfalfa':"#645a8c", 'Trigo':"#878a8f", 'Limón mexicano':"#66923d", 'Frijol':"#3bb9b8", 'Naranja dulce Valencia':"ffb566"}
        fig_states = px.bar(counter_data, x="ent", y="id", color="specie",color_discrete_map=colorsIdx,labels={"id": "Número de solicitudes","specie": "Especie", "ent": "Entidad"})
    except KeyError: 
        st.subheader('Intenta con otros Parámetros')
    else:
        st.markdown('**Solicitudes aprovadas por entidad federativa**')
        st.plotly_chart(fig_states)
        st.markdown('_Cada bloque dentro de la barra representan a un municipio distinto dentro de la Entidad Federativa_')

#Gráfico Superficies
    data_area = filtered_data.groupby(['specie']).mean()[['area']].dropna().reset_index()
    mini_counter= filtered_data.groupby(['specie']).count()[['id']].reset_index()
    data_area["color"] = data_area["specie"].map(colorsIdx)
    data_area = pd.merge(data_area, mini_counter, left_on='specie', right_on='specie', how='left')

    fig_area = px.scatter(data_area, x="area", y="specie",color="specie",color_discrete_map=colorsIdx, size="id", labels={"area":"Superficie aprobada (ha)", "id":"Número de Solicitudes","specie":"Organismo"})
    
    st.markdown('**Superficie promedio aprovada por solicitud de liberación al ambiente de OGM**')
    st.plotly_chart(fig_area)
    st.markdown('_El tamaño del circulo representa el número de solicitudes_')
# Gráfico características
    data_caract = filtered_data[['PROMOVENTE','EVENTO','specie','Resistencia_Insectos','Tolerancia_Glufosinato','Tolerancia_Glifosato','Tolerancia_Dicamba']]
    data_caract["color"] = data_caract["specie"].map(colorsIdx)
    fig_caract = px.parallel_categories(data_caract, dimensions=['EVENTO','Resistencia_Insectos','Tolerancia_Glufosinato','Tolerancia_Glifosato','Tolerancia_Dicamba'], color="color",width=900, labels={"EVENTO": "Evento transgénico","specie": "Especie", "Resistencia_Insectos": "Resistencia a insectos","Tolerancia_Glufosinato": "Tolerancia a glufosinato","Tolerancia_Glifosato":"Tolerancia al glifosato","Tolerancia_Dicamba":"Tolerancia a Dicamba"})
    
    st.markdown('**Carácterísticas fenotípicas de las distintas solicitudes de liberación al ambiente**')
    st.image(legend,use_column_width=True)
    st.plotly_chart(fig_caract)

# About

st.sidebar.markdown('''
> _**Acerca de esta información**_

> *Toda la información publicada en esta página forma parte del Registro Nacional de Bioseguridad de los Organismos Genéticamente Modificados.*
''')

url = 'https://www.conacyt.gob.mx/cibiogem/index.php/solicitudes/permisos-de-liberacion/solicitudes-de-permisos-de-liberacion-2020'

if st.sidebar.button('Ir al Registro Nacional de Bioseguridad de OGM'):
    webbrowser.open_new_tab(url)

