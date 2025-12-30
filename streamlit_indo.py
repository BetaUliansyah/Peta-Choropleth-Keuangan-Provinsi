# Data Source: https://public.tableau.com/app/profile/federal.trade.commission/viz/FraudandIDTheftMaps/AllReportsbyState
# US State Boundaries: https://public.opendatasoft.com/explore/dataset/us-state-boundaries/export/

import streamlit as st
import pandas as pd
pd.options.display.float_format = "{:,.2f}".format

import folium
from streamlit_folium import st_folium
import geopandas as gpd
from folium.features import GeoJsonTooltip
from folium import Map, TileLayer, Choropleth
import altair as alt

APP_TITLE = 'Peta Keuangan Provinsi'
APP_SUB_TITLE = 'Data BPS, DJPK dan BIG'

def mapping_file():
    map_file = {
        'IPM': 'data/ipm-indonesia.csv',
        'PDRB': 'data/pdrb-indonesia.csv',
        'APBD': 'data/apbd-indonesia.csv',
        'TKDD': 'data/tkdd-indonesia.csv',
    }
    return map_dict

def display_time_filters(df):
    year_list = list(df['tahun'].unique())
    year_list.sort()
    year = st.sidebar.selectbox('Tahun', year_list, len(year_list)-1)
    # quarter = st.sidebar.radio('Quarter', [1, 2, 3, 4])
    # st.header(f'{year}')
    return year

def display_state_filter(df, state_name):
    df = df.loc[(df['kode_wilayah'].astype(str).str[-2:] == '00')]
    state_list = [''] + list(df['wilayah'].unique())
    state_list.sort()
    state_index = state_list.index(state_name) if state_name and state_name in state_list else 0
    return st.sidebar.selectbox('Provinsi', state_list, state_index)

def display_top_slider():
    return True

def display_data_filter():
    return st.sidebar.radio('Data', ['IPM', 'PDRB', 'APBD', 'TKDD'], index=0)
    
def display_axis_y_filter():
    return st.sidebar.radio('Data Axis Y', ['IPM', 'PDRB', 'APBD', 'TKDD'], index=1)
    
def display_map(df, year, top_slider=5):
    st.header(f'Peta IPM tahun {year}')
    df = df[(df['tahun'] == year)]

    # merged geojson and df
    # Ensure both DataFrames have the same data type for the merge key
    map_gpd = gpd.read_file('map/indonesia_38_provinsi_bps.geojson')
    map_gpd['kode_wilayah'] = map_gpd['kode_wilayah'].astype(str)
    df['kode_wilayah'] = df['kode_wilayah'].astype(str)
    df_subset_tahun = df.loc[(df['tahun'] == year)]
    merged_df = map_gpd.merge(df_subset_tahun, left_on='kode_wilayah', right_on='kode_wilayah', how='left')

    map = folium.Map(location=[-2.5489, 118.0149], zoom_start=4, scrollWheelZoom=False, tiles = 'CartoDB positron')
    
    choropleth = folium.Choropleth(
        geo_data=merged_df,
        name="IPM Provinsi",
        data=merged_df,
        columns=["kode_wilayah", "nilai"],
        key_on="feature.properties.kode_wilayah",
        fill_color="YlGn",
        fill_opacity=0.8,
        line_opacity=1,
        line_weight=0.5,
        # line_opacity=0.8,
        highlight=True
    )
    choropleth.geojson.add_to(map)

    # Menambahkan Tooltip pada peta
    tooltip = GeoJsonTooltip(
        fields=["WADMPR", "kode_wilayah", "nilai"], # dari map geojson
        aliases=["Provinsi :", "Kode Provinsi:", "IPM:"], # dari map geojson juga
        style=(
            """background-color: #fdfdfd;
            color: #2f2f2f;
            font-family: arial;
            font-size: 12px;
            padding: 10px;"""
        ),
    )
    choropleth.geojson.add_child(tooltip)

    # Menambahkan marker top 5
    top_5 = merged_df.loc[(merged_df['tahun'] == year)].sort_values(by=['nilai'], ascending=False).head(5)
    top_5.to_crs("EPSG:4326")
    top_5["centroid"] = top_5.centroid
    for i in range(0,len(top_5)):

    top_df = merged_df.loc[(merged_df['tahun'] == year)].sort_values(by=['nilai'], ascending=False).head(top_slider)
    top_df["centroid"] = top_df.centroid
    for i in range(0,len(top_df)):
        # cari centroid dulu
        lat = top_df.iloc[i]["centroid"].y
        lon = top_df.iloc[i]["centroid"].x

    # https://python-graph-gallery.com/312-add-markers-on-folium-map/
        popup_text = f"{top_df.iloc[i]['wilayah']}: {top_df.iloc[i]['nilai']}"
        folium.Marker(
          location=[lat, lon],
          popup=popup_text,
          # icon=folium.DivIcon(html=f"""<div style="font-family: courier new; color: blue">{str(i+1)}</div>""")
          icon=folium.Icon(icon=f'{str(i+1)}', prefix='fa')
        ).add_to(map)
        
    df_indexed = df.set_index('wilayah')
    for feature in choropleth.geojson.data['features']:
        state_name = feature['properties']['WADMPR']
        # feature['properties']['population'] = 'Population: ' + '{:,}'.format(df_indexed.loc[state_name, 'State Pop'][0]) if state_name in list(df_indexed.index) else ''
        # feature['properties']['per_100k'] = 'Reports/100K Population: ' + str(round(df_indexed.loc[state_name, 'Reports per 100K-F&O together'][0])) if state_name in list(df_indexed.index) else ''

    #choropleth.geojson.add_child(
    #    folium.features.GeoJsonTooltip(['name', 'population', 'per_100k'], labels=False)
    #)
    
    st_map = st_folium(map, width=700, height=450)

    state_name = ''
    if st_map['last_active_drawing']:
        state_name = st_map['last_active_drawing']['properties']['wilayah']
    return state_name

def display_ranking(df, year, state_name=''):
    st.header(f'Ranking IPM {state_name} tahun {year}')
    df = df[(df['tahun'] == year) & (df['kode_wilayah'].astype(str).str[-2:] == '00')].sort_values(by=['nilai'], ascending=False)
    
    # mewarnai berbeda utk state_name
    #if state_name:
    #    df.loc[(df['wilayah'] == state_name)]
    df.reset_index(drop=True)
    bar_df = df.sort_values(by=['nilai'], ascending=False)
    st.write(alt.Chart(bar_df).mark_bar().encode(
    x=alt.X('nilai'),
    y=alt.X('wilayah', sort=None)))
    
def display_trend(df, state_name):
    if state_name == '':
        st.warning(f'Pilih daerah terlebih dahulu')    
    tahun_awal = df['tahun'].min()
    tahun_akhir = df['tahun'].max()
    st.header(f'Trend IPM {state_name} tahun {tahun_awal}-{tahun_akhir}')
    # indonesia_df = df[(df['kode_wilayah'] == 9999)].sort_values(by=['tahun'], ascending=True)
    df = df[(df['wilayah'] == state_name)].sort_values(by=['tahun'], ascending=True)
    # df['nilai_indonesia']=indonesia_df['nilai']
    # df.sort_values(by=['nilai'], ascending=False)
    # df.drop(df['judul_data'])
    df.reset_index(drop=True)
    st.line_chart(data=df, x="tahun", y="nilai")
    # st.bar_chart(data=df, x="wilayah", y="nilai", horizontal=True)
    # st.table(df)

def display_scatterplot(df1, df2, state_name):
    df1 = df1[(df1['wilayah'] == state_name)].sort_values(by=['tahun'], ascending=True)
    df2 = df2[(df2['wilayah'] == state_name)].sort_values(by=['tahun'], ascending=True)
    chart_data = df1.merge(df2, left_on='tahun', right_on='tahun', how='left')
    
    st.scatter_chart(chart_data, x="wilayah_x", y=["nilai_x", "nilai_y"])  
    
def display_facts(df, year, state_name, field, title, string_format='${:,}', is_median=False):
    df = df[(df['tahun'] == year)]
    if state_name:
        df = df[df['wilayah'] == state_name]
    df.drop_duplicates(inplace=True)
    if is_median:
        total = df[field].sum() / len(df[field]) if len(df) else 0
    else:
        total = df[field].sum()
    st.metric(title, string_format.format(round(total)))

def display_all_df():
    df_ipm = pd.read_csv('data/ipm-indonesia.csv', index_col=None)
    table_ipm = df_ipm.head(5)
    st.table(table_ipm)
    map_gpd = gpd.read_file('data/indonesia_38_provinsi.json')
    columns_map = map_gpd.columns
    st.write(columns_map)
    table_map = map_gpd[['KDPPUM', 'WADMPR', 'kode_wilayah']]
    st.table(table_map)
    daerah_ipm = df_ipm.loc[(df_ipm['tahun'] == 2024) & (df_ipm['kode_wilayah'].astype(str).str[-2:] == '00')][['kode_wilayah', 'wilayah']]
    st.table(daerah_ipm)
    

def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    # map file
    map_file = {
        'IPM': 'data/ipm-indonesia.csv',
        'PDRB': 'data/pdrb-indonesia.csv',
        'APBD': 'data/apbd-indonesia.csv',
        'TKDD': 'data/tkdd-indonesia.csv',
    }

    # Load Data awal dan menampilkan filter
    data = display_data_filter()  
    axis_y = display_axis_y_filter()
    top_slider = st.sidebar.slider("Top Tooltip", 0, 9, 5) # gmn biar bisa 38 prov
    # top_slider = display_top_slider(df_ipm)

    
    'IPM' if data == ''
    filename = map_file.get(data)
    df = pd.read_csv(filename, index_col=None)
    year = display_time_filters(df)
    state_name = display_map(df, year, top_slider)
    
    # tab
    tab1, tab2, tab3, tab4 = st.tabs(["charts", "trends", "scatter plot", "debug"])
    with tab1:
        display_ranking(df, year, state_name)
    with tab2:
        display_trend(df, state_name)
    with tab3:
        display_scatterplot(df_ipm, df_pdrb, state_name)
    with tab4:
        display_scatterplot(df, df_pdrb, state_name)
    
    #Display Filters and Map
    
    # state_name = display_map(df_ipm, year)
    
    # display_ranking(df_ipm, year)

    #debug
    st.warning(f'state_name: {state_name}, year: {year}, data: {data}, axis_y: {axis_y}')
    
    

    #Display Metrics
    st.subheader(f'Data Provinsi {state_name}')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        display_facts(df_ipm, year, state_name, 'nilai', f'# of Reports', string_format='{:,}')
    with col2:
        display_facts(df_ipm, year, state_name, 'nilai', f'# of Reports', string_format='{:,}')
        #tab1, tab2, tab3, tab4 = st.tabs(["maps", "charts", "trends", "scatter plot"])
        #with tab1:
        #    state_name = display_map(df_ipm, year)
        #with tab2:
        #    display_ranking(df_ipm, year)
        #with tab3:
        #    print("Test")
        #with tab4:
        #    print("Test")
    with col3:
        display_facts(df_ipm, year, state_name, 'nilai', f'Nilai IPM', string_format='{:,}')


if __name__ == "__main__":
    main()
