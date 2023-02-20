import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as clrs
import geopandas as gpd
import streamlit as st
import folium
from streamlit_folium import st_folium

def create_barplot(x, y, title_text):
    fig = go.Figure(go.Bar(
        x=x,
        y=y,
        orientation='h',
        text=x,
        textfont=dict(color="white"),
        marker_color=clrs.qualitative.Antique[9],
        hovertemplate='%{y}: %{x} <extra></extra>',
    ))
    fig.update_layout(
        title=dict(
            text=f'{title_text} <br>(from {min_date} to {max_date})',
            font=dict(
                color='white'
                )
            ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            visible=False,
            
        ),
        yaxis=dict(
            tickmode="array",
            categoryorder="total ascending",
            tickvals=y,
            ticktext=y,
            ticklabelposition="inside",
            tickfont=dict(color="white"),
        ),
        height=850
    )
    return fig



oblast_data_url = 'https://raw.githubusercontent.com/Vadimkin/ukrainian-air-raid-sirens-dataset/main/datasets/volunteer_data_uk.csv'

oblast_alerts_df = pd.read_csv(oblast_data_url, index_col=0)
oblast_alerts_df.reset_index(inplace=True)

name_map = {
    'Київ': 'Kyiv',
    'Черкаська область': 'Cherkasy Oblast',
    'Запорізька область': 'Zaporizhzhia Oblast',
    'Вінницька область': 'Vinnytsia Oblast',
    'Рівненська область': 'Rivne Oblast',
    'Волинська область': 'Volyn Oblast',
    'Харківська область': 'Kharkiv Oblast',
    'Львівська область': 'Lviv Oblast',
    'Херсонська область': 'Kherson Oblast',
    'Одеська область': 'Odesa Oblast',
    'Житомирська область': 'Zhytomyr Oblast',
    'Чернігівська область': 'Chernihiv Oblast',
    'Сумська область': 'Sumy Oblast',
    'Миколаївська область': 'Mykolaiv Oblast',
    'Хмельницька область': 'Khmelnytskyi Oblast',
    'Тернопільська область': 'Ternopil Oblast',
    'Київська область': 'Kyiv Oblast',
    'Донецька область': 'Donetsk Oblast',
    'Дніпропетровська область': 'Dnipropetrovsk Oblast',
    'Івано-Франківська область': 'Ivano-Frankivsk Oblast',
    'Полтавська область': 'Poltava Oblast',
    'Кіровоградська область': 'Kirovohrad Oblast',
    'Чернівецька область': 'Chernivtsi Oblast',
    'Луганська область': 'Luhansk Oblast',
    'Закарпатська область': 'Zakarpattia Oblast',
    'Автономна Республіка Крим': 'Autonomous Republic of Crimea',
}

oblast_alerts_df.region = oblast_alerts_df.region.apply(lambda x: name_map[x])
oblast_alerts_df['started_at'] = pd.to_datetime(oblast_alerts_df['started_at'])
oblast_alerts_df['finished_at'] = pd.to_datetime(oblast_alerts_df['finished_at'])

min_date = min(oblast_alerts_df['started_at']).strftime("%Y-%m-%d")
max_date = max(oblast_alerts_df['started_at']).strftime("%Y-%m-%d")

oblast_alerts_df['duration'] = (oblast_alerts_df['finished_at'] - oblast_alerts_df['started_at'])


st.set_page_config(page_title='Air Alerts in Ukraine', layout="wide")

longest_alert = oblast_alerts_df.iloc[oblast_alerts_df['duration'].argmax()]
longest_alert.started_at.date().strftime('%Y-%m-%d')

longest_alert_string=f'The longest Air Alert (excluding Luhansk Oblast) started in {longest_alert.region}, \
{longest_alert.started_at.date().strftime("%Y-%m-%d")} and lasted {longest_alert.duration.days} days, \
{longest_alert.duration.seconds//3600} hours and {(longest_alert.duration.seconds//60)%60} minutes'


oblast_alerts_df['started_at_day'] = oblast_alerts_df['started_at'].dt.date
grouped = oblast_alerts_df.groupby(['region', 'started_at_day']).agg({'duration':['count', 'sum']})
max_alerts = grouped.iloc[grouped.duration['count'].argmax()]

max_alerts_string = f"On {max_alerts.name[1].strftime('%Y-%m-%d')}, \
there were {max_alerts.duration['count']} Air Alers in {max_alerts.name[0]}, \
for a total duration of {max_alerts.duration['sum'].seconds//3600} hours and {(max_alerts.duration['sum'].seconds//60)%60} minutes"




total_alerts = oblast_alerts_df['region'].value_counts()
total_alerts_by_region = pd.DataFrame(total_alerts.reset_index().rename(columns={'index':'region', 'region': 'count'}))
oblast_alerts_df['duration_seconds'] = oblast_alerts_df.duration.apply(lambda x: x.total_seconds())


geo_regions = gpd.read_file('ukraine_regions.geojson')
geo_regions.rename(columns={'region_en': 'region'}, inplace=True)
del geo_regions['region_ua']
total_duration_by_region = oblast_alerts_df.groupby('region')['duration'].sum()
total_duration_by_region = pd.DataFrame(total_duration_by_region.reset_index())
df_sum_geo = pd.concat([geo_regions.set_index('region'), total_alerts_by_region.set_index('region'), total_duration_by_region.set_index('region')], axis=1)
df_sum_geo = df_sum_geo.astype({"duration": "str"})
df_sum_geo["duration"] = df_sum_geo["duration"].replace({"NaT": "N/A"})

st.markdown("<h1 style='text-align: center; color: #8c785d;'>rUSSIAN INVASION OF UKRAINE</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #8c785d;'>Air Alerts</h2>", unsafe_allow_html=True)

with st.container():
    map = folium.Map(
        location=[50, 35],
        tiles="cartodbpositron",
        zoom_start=6,
        dragging=False,
        zoom_control=False,
        scrollWheelZoom=False,
    )
    folium.Choropleth(
        geo_data=df_sum_geo.__geo_interface__,
        data=total_alerts,
        key_on="feature.id",
        fill_color="RdYlGn_r",
        bins=12,
        legend_name=f"Total number of air alerts (from {min_date} to {max_date})"
    ).add_to(map)
    style_function = lambda x: {
        "fillOpacity": 0,
        "color": "#000000",
        "weight": 1.8,
    }
    highlight_function = lambda x: {
        "fillColor": 'white',
        "fillOpacity": 0.5,
        "color": "#000000",
        "weight": 1.8,
    }
    df_sum_geo.reset_index(inplace=True)
    folium.features.GeoJson(
        data=df_sum_geo.__geo_interface__,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=["region", "count", "duration"],
            aliases=["Region", "Total number of Alerts", "Total duration of Alerts"],
            sticky=False
        )
    ).add_to(map)

    
    st_map = st_folium(map,height=850, width=2200)



with st.container():
    st.markdown(f"<h3 style='text-align: center; color: #8c785d;'>{max_alerts_string}</h1>", unsafe_allow_html=True)
    st.plotly_chart(create_barplot(total_alerts_by_region['count'], 
                                   total_alerts_by_region['region'],
                                   'Total number of Alerts'), use_container_width=True)


with st.container():
    total_duration_by_region = oblast_alerts_df.groupby('region')['duration_seconds'].sum()
    total_duration_by_region = pd.DataFrame(total_duration_by_region.reset_index())

    st.markdown(f"<h3 style='text-align: center; color: #8c785d;'>{longest_alert_string}</h1>", unsafe_allow_html=True)
    st.plotly_chart(create_barplot((total_duration_by_region['duration_seconds']/3600).round(2), 
                                    total_duration_by_region['region'],
                                    'Total duration of Alerts, hours'), use_container_width=True)