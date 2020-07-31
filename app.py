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
from bokeh.models.widgets import Div
from streamlit import caching
import SessionState

#styling
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

# Archivos principales
path = "resoluciones_db_geo_29062020.csv"

# Leyendo datos de resoluciones

data_gmo = pd.read_csv(path, encoding ="latin-1")

# Cargando imágenes

legend = Image.open('legend_atlas.png')
logo = Image.open('logo_cibiogem.png')

# Transform color maps

COLORS_R = {"Algodón": 190, "Maíz": 236, "Soya":153, "Alfalfa":101, "Trigo":135, "Limón mexicano":102, "Frijol":59, "Naranja dulce Valencia":255}

COLORS_G = {"Algodón": 169, "Maíz": 228, "Soya":185, "Alfalfa":74, "Trigo":138, "Limón mexicano":146, "Frijol":185, "Naranja dulce Valencia":181}

COLORS_B = {"Algodón": 146, "Maíz": 86, "Soya":152, "Alfalfa":140, "Trigo":143, "Limón mexicano":61, "Frijol":216, "Naranja dulce Valencia":102}

data_gmo["color_r"] = data_gmo["specie"].map(COLORS_R)
data_gmo["color_g"] = data_gmo["specie"].map(COLORS_G)
data_gmo["color_b"] = data_gmo["specie"].map(COLORS_B)

st.image(logo,use_column_width=True)
st.markdown('''# *Ecosistema Nacional Informático de Bioseguridad de los Organismos Genéticamente Modificados*

## *ENI-Bioseguridad*

La Secretaría Ejecutiva de la CIBIOGEM, desarrolla y actualiza el Sistema Nacional de Información sobre Bioseguridad (SNIB) 
y el Registro Nacional de Bioseguridad de los OGM (RNB), ambas plataformas están dedicadas a reunir y sintetizar documentos y 
bases de datos relevantes en materia de bioseguridad. 
El presente Ecosistema Informático de Bioseguridad muestra la información geográfica y estadística de todas las solicitudes de 
liberación al ambiente con resolución favorable (permisos de liberación) entre los años 2005 y 2018 en cualquiera de sus 
fases (Experimental, Programa Piloto y Comercial).
*Toda la información publicada en esta página forma parte del RNB.* ''')

update = "24/07/2020"
st.write('''_Fecha de la última actualización:_''', update)

# Selectores de información

st.sidebar.subheader('Parámetros de búsqueda')

st.sidebar.markdown('''
Empleando los siguientes controles usted podrá filtrar y seleccionar todas las solicitudes de liberación al
 ambiente de Organismos Genéticamente Modificados (OGMs) con resolución favorable que figuran en el Sistema Nacional de Información sobre Bioseguridad desde 2005 a 2018. 
 Cada solicitud puede ser seleccionada por ```Tipo``` de liberación, ```Año``` de la solicitud y ```Organismo``` de la solicitud.''')

#Sesión y parametros widget
session_state = SessionState.get(year_button=False, specie_button=False, year_id=0, specie_id=0)

st.sidebar.markdown("**Año de la solicitud**")
year_button = st.sidebar.button('Incluir todos los años')
if year_button:
    session_state.year_button = True
    session_state.year_id += 1
if session_state.year_button:
    year_to_filter = st.sidebar.multiselect('Elije uno o más años de la lista',[2020, 2019]+list(data_gmo['year'].unique()), default=[2020, 2019]+list(data_gmo['year'].unique()),key=session_state.year_id)
else:
    year_to_filter = st.sidebar.multiselect('Elije uno o más años de la lista',[2020, 2019]+list(data_gmo['year'].unique()), default=[2005])

st.sidebar.markdown("**Tipo de liberación**")
type_filter = st.sidebar.multiselect('Elije uno o más tipos de liberación',list(data_gmo['type'].unique()), default=['Experimental'])

st.sidebar.markdown("**Organismo de la solicitud**")
specie_button = st.sidebar.button('Incluir todos los organismos')
if specie_button:
    session_state.specie_button = True
    session_state.specie_id += 1
    
if session_state.specie_button:
    specie_filter = st.sidebar.multiselect('Elije uno o varios organismos de la solicitud', list(data_gmo['specie'].unique()),default=list(data_gmo['specie'].unique()),key=session_state.specie_id)

else:
    specie_filter = st.sidebar.multiselect('Elije uno o varios organismos de la solicitud', list(data_gmo['specie'].unique()),default=['Algodón','Maíz','Soya'])

st.sidebar.markdown("**Sobre las solicitudes de maíz GM**")
st.sidebar.info('''
*Todo el proceso de otorgamiento de permisos y todas las actividades para la liberación al ambiente de maíz genéticamente modificado, es decir la siembra en cualquier fase, 
están suspendidas desde 2013 como parte de las medidas cautelares por la demanda de acción colectiva interpuesta en contra de varias dependencias del Ejecutivo Federal. 
No obstante, sí están permitidas las autorizaciones para consumo y los avisos de utilización confinada, es por ello que se sigue importando maíz GM y procesando para 
alimentos de consumo humano y animal.
''')

st.sidebar.markdown('**Sobre la solicitud de liberación de soya 007/2012**')
st.sidebar.info('''
En el 2012 la Secretaría de Agricultura, Ganadería, Desarrollo Rural, Pesca y Alimentación (SAGARPA, hoy Secretaría de Agricultura y 
Desarrollo Rural, SADER) expidió el permiso de liberación al ambiente de soya genéticamente modificada B00.04.03.02.01.-4377. para 
varios municipios de los estados de Campeche, Chiapas, Quintana Roo, San Luis Potosí, Tamaulipas, Veracruz y Yucatán, derivado de la 
solicitud de liberación al ambiente en fase comercial número 007/2012. Sin embargo, se interpusieron recursos administrativos y
 judiciales pendientes de resolver en la actualidad, por lo que las actividades relativas a dicho permiso se encuentran detenidas.
''')

st.sidebar.markdown('**Sobre las solicitudes 2019-2020**')
st.sidebar.markdown('''
A la última fecha de actualización el _RNB_ no cuenta con solicitudes de liberación con resolución favorable para los años
2019 y 2020
''')

filtered_data = data_gmo[data_gmo.year.isin(year_to_filter)]
filtered_data = filtered_data[filtered_data.type.isin(type_filter)]
filtered_data= filtered_data[filtered_data.specie.isin(specie_filter)]

#Base de datos por solicitud

solic_data_raw = filtered_data.groupby(['SOLICITUD']).count()[['id']].reset_index()

solic_data_ents = pd.merge(solic_data_raw, filtered_data[['SOLICITUD','ent','specie','ORGANISMO','year','type','area','PROMOVENTE','EVENTO','Fenotip','color_r','color_g','color_b']], left_on='SOLICITUD', right_on='SOLICITUD', how='left')

solic_data = solic_data_ents.drop_duplicates(subset=['SOLICITUD']).reset_index(drop=True)

#Base de datos geográfica

counter_data_raw = filtered_data.groupby(['cvgeo','specie','type']).count()[['id']].reset_index()

counter_data_merge = pd.merge(counter_data_raw, filtered_data[['cvgeo','mun','ent','ORGANISMO','year','lat','lon','color_r','color_g','color_b']], on='cvgeo')

counter_data = counter_data_merge.drop_duplicates(subset=['cvgeo','type','specie']).reset_index(drop=True)

# Creación de Mapa y gráficos

if not counter_data.size:
    st.subheader('No se encontró ningún registro con los parámetros de busqueda ingresados, intenta otros parámetros')
else:
    table_solic = solic_data[['SOLICITUD','specie','ORGANISMO','year','type','area','PROMOVENTE','EVENTO','Fenotip']]
    table_solic.columns = ['Solicitud','Especie','Nombre científico','Año','Tipo de solicitud','Area aprobada (ha)','Promovente','Evento','Características']
    table_data = counter_data[['id','mun','ent','specie','ORGANISMO','type']]
    table_data.columns = ['Número de solicitudes','Municipio','Entidad','Especie','Nombre científico','Tipo de solicitud']

    # Descripción de los datos mostrados
    st.write('**Se muestran todas las solicitudes de liberación con resolución favorable de los siguientes años:**')
    st.info(', '.join(map(str,year_to_filter)))
    st.write('**De los siguientes tipos de liberación:**')
    st.info(', '.join(type_filter))
    st.write('**Y de los siguientes organismos:**')
    st.info(', '.join(specie_filter))

    st.markdown('''
    **Tabla de solicitudes de liberación al ambiente con resolución favorable**
    
    La siguiente tabla muestra las diferentes solicitudes que cumplen con los criterios de búsqueda. Adicionalmente, se detalla, el código de la solicitud, la especie,
     el año de la solicitud, el tipo de liberación, el área aprobada, el promovente, el evento transgénico y las características del organismo. Puedes emplear las barras laterales para desplazarte en la 
     tabla y el icono de las flechas en la esquina superior derecha de la tabla
     para mostrar la información en pantalla completa.''')

    st.write(table_solic)

    st.markdown('''Para mas información y detales sobre las distintas solicitudes de liberación al ambiente puede visitar el Registro Nacional de Bioseguridad de los OGM (RNB):''')

    if st.button('Ir al Registro Nacional de Bioseguridad de los OGM'):
        js = "window.open('https://www.conacyt.gob.mx/cibiogem/index.php/solicitudes/permisos-de-liberacion/solicitudes-de-permisos-de-liberacion-2020')"  # New tab or window
    html = '<img src onerror="{}">'.format(js)
    div = Div(text=html)
    st.bokeh_chart(div)

    st.markdown('''
    ---
    ## **Resumen de las solicitudes de liberación seleccionadas desglosadas por municipio**''')

    st.markdown('''
    **Ubicación geográfica de las solicitudes de liberación al ambiente**
    
    El mapa muestra la ubicación geográfica de las solicitudes de liberación desglosadas por municipio (una solicitud puede incluir a varios municipios). Puedes
    posicionar el cursor sobre cada punto para conocer información adicional.
    El ancho del circulo corresponde al número de solicitudes desglosadas por municipio, cada circulo fue asociado al centroide del municipio.''')

    #Mapa
    st.image(legend,use_column_width=True)
    st.info('*La leyenda muestra la cromática de todos los cultivos disponibles en la base de datos.*')
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
            get_radius="id*700",
            get_fill_color=['color_r', 'color_g', 'color_b'],
            hover=True,
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
#Tabla por municipio
    st.markdown('''
    **Tabla de solicitudes de liberación desglosadas por municipio**
    
    La siguiente tabla muestra el número de solicitudes desglosada por municipio. Adicionalmente, se detalla la especie y el tipo de solicitud. 
    Puedes emplear las barras laterales para desplazarte en la tabla y el icono de las flechas en la esquina superior derecha de la tabla
     para mostrar la información en pantalla completa.''')
    st.write(table_data)

# Gráfico por estados
    try: 
        colorsIdx = {'Algodón': '#bea992', 'Maíz': '#ece556','Soya':"#99b998", 'Alfalfa':"#645a8c", 'Trigo':"#878a8f", 'Limón mexicano':"#66923d", 'Frijol':"#3bb9b8", 'Naranja dulce Valencia':"#ffb566"}
        fig_states = px.bar(counter_data, x="ent", y="id", color="specie",color_discrete_map=colorsIdx,labels={"id": "Número de solicitudes por Mun.","specie": "Especie", "ent": "Entidad", "mun": "Municipio"})
    except KeyError: 
        st.subheader('Intenta con otros Parámetros')
    else:
        st.markdown('''
        **Solicitudes aprobadas por entidad federativa**

        El gráfico muestra el agregado de solicitudes aprobadas por municipio en cada entidad federativa, a partir de la tabla anterior. Cada bloque dentro de la barra representa el agregado de solicitudes
        con resolución favorable para un determinado municipio.
        ''')
        st.plotly_chart(fig_states)

#Gráfico Superficies
    st.markdown('''
    ---
    ## **Información adicional sobre las solicitudes de liberación**''')
    data_area = solic_data.groupby(['specie']).mean()[['area']].dropna().reset_index()
    mini_counter= solic_data.groupby(['specie']).count()[['id']].reset_index()
    data_area["color"] = data_area["specie"].map(colorsIdx)
    data_area = pd.merge(data_area, mini_counter, left_on='specie', right_on='specie', how='left')

    fig_area = px.scatter(data_area, x="area", y="specie",color="specie",color_discrete_map=colorsIdx, size="id", labels={"area":"Superficie aprobada promedio (ha)", "id":"Número de Solicitudes","specie":"Organismo"})
    
    st.markdown('''
    **Superficie aprobada promedio por solicitud de liberación al ambiente de OGMs**
    
    El gráfico muestra la media de superficie aprobada considerando todas las solicitudes del mismo organismo.
    El tamaño del circulo representa el número de solicitudes.''')
    st.plotly_chart(fig_area)
# Gráfico características
    data_caract = filtered_data[['SOLICITUD','PROMOVENTE','EVENTO','specie','Resistencia_Insectos','Tolerancia_Glufosinato','Tolerancia_Glifosato','Tolerancia_Dicamba']]
    data_caract["color"] = data_caract["specie"].map(colorsIdx)
    data_caract = data_caract.drop_duplicates(subset=['SOLICITUD']).reset_index(drop=True)
    

    fig_caract = px.parallel_categories(data_caract,dimensions=['EVENTO','Resistencia_Insectos','Tolerancia_Glufosinato','Tolerancia_Glifosato','Tolerancia_Dicamba'], color="color",width=900,labels={"EVENTO": "Evento transgénico","specie": "Especie", "Resistencia_Insectos": "Resistencia a insectos","Tolerancia_Glufosinato": "Tolerancia a glufosinato","Tolerancia_Glifosato":"Tolerancia al glifosato","Tolerancia_Dicamba":"Tolerancia a Dicamba"})
    fig_caract.update_layout(margin=dict(l=150, r=15, b=40, t=40))

    st.markdown('''
    **Características fenotípicas de las distintas solicitudes de liberación al ambiente**
    
    El gráfico muestra el número de solicitudes agrupadas según el evento transgénico y sus características de resistencia a insectos o 
    tolerancia a herbicidas. Cada atributo está representado por una columna de rectángulos. El tamaño de cada rectángulo refleja el 
    número de solicitudes que presentó o no una característica determinada, además cada organismo posee un color distinto. 
    Al posicionar el cursor en cada segmento de la barra se muestra el número de solicitudes que poseen dicha característica bajo la leyenda: *Cuenta* (```Count```).''')
    st.image(legend,use_column_width=True)
    st.plotly_chart(fig_caract)