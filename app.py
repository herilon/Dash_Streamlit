import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pydeck
from datetime import datetime

#@st.cache_data
def cargar_contagios():
    data = pd.read_excel('streamlitcovid.xlsx', sheet_name='contagios')
    return data

#@st.cache_data
def cargar_departamentos():
    data = pd.read_excel('streamlitcovid.xlsx', sheet_name='departamento')
    return data

df_contagios = cargar_contagios()
df_departamentos = cargar_departamentos()

df_join = df_contagios.join(df_departamentos.set_index('departamento'), on='departamento', validate='m:1')
df_join['fecha_diagnostico'] = df_join['fecha_diagnostico'].str[:10]
df_join['fecha_muerte'] = df_join['fecha_muerte'].str[:10]

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Datos", "Lineas", "Barras", "Mapa", "Circular", "Histograma"])

with tab1:
    ver_df = st.toggle('Ver DataFrame', value=True)
    if ver_df:
        st.write(df_join)

    #KPI
    confirmados = df_join.id_de_caso.count()
    recuperados = (df_join['recuperado'] == 'Recuperado').sum()
    fallecidos = (df_join['recuperado'] == 'Fallecido').sum()
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Casos confirmados", value=confirmados)
    col2.metric(label="Recuperados", value=recuperados)
    col3.metric(label="Fallecidos", value=fallecidos)

with tab2:
    # Gráfico de contagios por fecha

    with st.container(border=True):
        fecha1 = datetime.strptime(df_join['fecha_diagnostico'].min(), '%Y-%m-%d')
        fecha2 = datetime.strptime(df_join['fecha_diagnostico'].max(), '%Y-%m-%d')
        slider_fechas = st.slider(
            "Seleccione un rango de fechas", 
            min_value=fecha1, 
            max_value=fecha2, 
            value=(fecha1, fecha2)
        )
        valor1 = slider_fechas[0].strftime('%Y-%m-%d')
        valor2 = slider_fechas[1].strftime('%Y-%m-%d')
        df_filtro_contagio_fecha = df_join[(df_join['fecha_diagnostico'] >= valor1) & (df_join['fecha_diagnostico'] <= valor2)]

        df_contagios_fecha = df_filtro_contagio_fecha.groupby(['fecha_diagnostico']).count()['id_de_caso']
        
        st.header('Contagios x Fecha')
        st.line_chart(df_contagios_fecha, x_label='Fecha', y_label='Cantidad')

    # Gráfico de fallecidos por fecha

    df_fallecidos = df_join[df_join['recuperado'] == 'Fallecido']
    df_fallecidos_fecha = df_fallecidos.groupby(['fecha_muerte']).count()['id_de_caso']
    with st.container(border=True):
        st.header('Fallecidos x Fecha')
        fig, ax = plt.subplots()
        ax.plot(df_fallecidos_fecha)
        ax.set_title('Fallecidos')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Cantidad')
        ax.tick_params(axis='x', labelrotation=90, labelsize=6)
        st.pyplot(fig)

with tab3:
    # Contagios por departamento

    df_contagios_departamento = df_join.groupby(['departamento_nom']).count()['id_de_caso']
    with st.container(border=True):
        st.header('Contagios x Departamento')
        st.bar_chart(df_contagios_departamento)

    # Fallecidos por departamento
    df_fallecidos_departamento = df_fallecidos.groupby(['departamento_nom']).count()['id_de_caso']
    with st.container(border=True):
        st.header('Fallecidos x Departamento')
        st.bar_chart(df_fallecidos_departamento, horizontal=True)


with tab4:
    # Mapa de contagios 1

    df_contagios_departamento_mapa = df_join.groupby(by=['departamento_nom', 'latitud','longitud'], as_index=False).id_de_caso.count()
    df_contagios_departamento_mapa['size'] = df_contagios_departamento_mapa['id_de_caso'] * 300
    with st.container(border=True):
        st.header('Mapa de contagios')
        st.map(df_contagios_departamento_mapa, latitude='latitud', longitude='longitud', size='size')

    capas=pydeck.Layer(
        "ScatterplotLayer",
        data=df_contagios_departamento_mapa,
        get_position=["longitud", "latitud"],
        get_color="[255, 75, 75]",
        pickable=True,
        auto_highlight=True,
        get_radius="size"
    )

    vista_inicial=pydeck.ViewState(
        latitude=4,
        longitude=-74,
        zoom=4.5,
    )

    with st.container(border=True):
        st.header('Mapa de contagios')
        st.pydeck_chart(
            pydeck.Deck(
                layers=capas,
                map_style=None,
                initial_view_state=vista_inicial,
                tooltip={"text": "{departamento_nom}\nContagios: {id_de_caso}"}
            )
        )

with tab5:
    # Grafico de contagios por sexo

    df_contagios_sexo = df_join.groupby(['sexo']).id_de_caso.count()
    fig, ax = plt.subplots()
    ax.pie(df_contagios_sexo, labels=df_contagios_sexo.index, autopct='%1.1f%%')
    with st.container(border=True):
        st.header('Contagios por Sexo')
        st.pyplot(fig) 

with tab6:
    # Histograma de edades

    fig, ax = plt.subplots()
    ax.hist(df_join['edad'])
    with st.container(border=True):
        st.header('Histograma por edades')
        st.pyplot(fig)

