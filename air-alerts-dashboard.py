import pandas as pd
import geopandas as gpd
import streamlit as st
import folium
from streamlit_folium import st_folium
from utility import(
    create_barplot,
    create_barplot2,
    create_barplot3,
    name_map,
    day_part_map,
    config_static
)

# Importing and loading Alerts data
oblast_data_url = 'https://raw.githubusercontent.com/Vadimkin/ukrainian-air-raid-sirens-dataset/main/datasets/volunteer_data_uk.csv'
oblast_alerts_df = pd.read_csv(oblast_data_url, index_col=0)
# Processing Alerts data
oblast_alerts_df.reset_index(inplace=True)
## renaming UA regions to EN 
oblast_alerts_df['region'] = oblast_alerts_df['region'].apply(lambda x: name_map[x]) 
## changist data types to datetine
oblast_alerts_df['started_at'] = pd.to_datetime(oblast_alerts_df['started_at'])
oblast_alerts_df['finished_at'] = pd.to_datetime(oblast_alerts_df['finished_at'])
## adding fields for further analysis
oblast_alerts_df['duration'] = (oblast_alerts_df['finished_at'] - oblast_alerts_df['started_at'])
oblast_alerts_df['started_at_day'] = oblast_alerts_df['started_at'].dt.date
oblast_alerts_df['duration_seconds'] = oblast_alerts_df['duration'].apply(lambda x: x.total_seconds())
oblast_alerts_df['started_hour'] = oblast_alerts_df['started_at'].dt.hour
## mapping starting hour to one of 6 day period bins 4 hours each
oblast_alerts_df['start_period'] = (oblast_alerts_df['started_hour']%24 + 4)//4
oblast_alerts_df['start_period'] = oblast_alerts_df['start_period'].apply(lambda x: day_part_map[x])
## if Alert was issued without previous Alert cancelation, then naive=True and finished_at = started_at + 30 min
del oblast_alerts_df['naive']

# Importing and loading geoJSON data
geo_regions = gpd.read_file('ukraine_regions.geojson')
geo_regions.rename(columns={'region_en': 'region'}, inplace=True)
del geo_regions['region_ua']

# Getting dates of first recorded Alert issue and most recent updated Alert issue
min_date = min(oblast_alerts_df['started_at']).strftime("%Y-%m-%d")
max_date = max(oblast_alerts_df['started_at']).strftime("%Y-%m-%d")

# Getting total number of Alerts issued by region
total_alerts = oblast_alerts_df['region'].value_counts()
total_alerts_by_region_df = pd.DataFrame(total_alerts.reset_index())

# Grouping by region and Alert issue datetime and aggregating duration field
grouped = oblast_alerts_df.groupby(['region', 'started_at_day']).agg({'duration':['count', 'sum']})
max_alerts = grouped.iloc[grouped.duration['count'].argmax()]

# Getting longest Alert entry
longest_alert = oblast_alerts_df.iloc[oblast_alerts_df['duration'].argmax()]

# Getting total duration in seconds of Alerts grouped by region
total_duration_seconds_by_region = oblast_alerts_df.groupby('region')['duration_seconds'].sum()
total_duration_seconds_by_region_df = pd.DataFrame(total_duration_seconds_by_region.reset_index())

# Getting total duration timestamp of Alert for map plot
total_duration_by_region = oblast_alerts_df.groupby('region')['duration'].sum()
total_duration_by_region_df = pd.DataFrame(total_duration_by_region.reset_index())

# Creating summary dataframe for map plot
df_sum_geo = pd.concat([geo_regions.set_index('region'), total_alerts_by_region_df.set_index('region'), total_duration_by_region_df.set_index('region')], axis=1)
df_sum_geo = df_sum_geo.astype({'duration': 'str'})
df_sum_geo['duration'] = df_sum_geo['duration'].replace({'NaT': 'N/A'})
## Fixinf Luhasnk Oblast duration
df_sum_geo.loc[df_sum_geo.eval('region == "Luhansk Oblast"'), 'duration'] = 'Ongoing'

# Counting total Alerts issued during each dat period
periods_total_df = oblast_alerts_df['start_period'].value_counts().reset_index()

# Getting amount of Alerts issued in each day period grouped by region
periods_grouped = oblast_alerts_df.groupby(['region','start_period']).size().reset_index()
periods_grouped.rename(columns = {
    0: 'count'
}, inplace=True)


st.set_page_config(page_title='Air Alerts in Ukraine', layout='wide')

st.markdown("<h1 style='text-align: center; color: #8c785d;'>rUSSIAN INVASION OF UKRAINE</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: #8c785d;'>Air Alerts<sup>1</sup></h2>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: #8c785d;'>from {min_date} to {max_date}</h3>", unsafe_allow_html=True)

# Displaying map chart
with st.container():
    map = folium.Map(
        location=[48.37, 31.16],
        tiles='cartodbpositron',
        zoom_start=6,
        max_bounds=True,
        # dragging=False,
        # zoom_control=False,
        scrollWheelZoom=False,
    )
    # map.fit_bounds([(44,22), (52,39.5)])
    folium.Choropleth(
        geo_data=df_sum_geo.__geo_interface__,
        data=total_alerts,
        key_on='feature.id',
        fill_color='RdYlGn_r',
        bins=12,
        legend_name='Total Alerts number'
    ).add_to(map)

    style_function = lambda x: {
        'fillOpacity': 0,
        'color': '#000000',
        'weight': 1.5,
    }
    highlight_function = lambda x: {
        'fillColor': 'white',
        'fillOpacity': 0.5,
        'color': '#000000',
        'weight': 1.5,
    }

    df_sum_geo.reset_index(inplace=True)

    folium.features.GeoJson(
        data=df_sum_geo.__geo_interface__,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.features.GeoJsonTooltip(
            fields=['region', 'count', 'duration'],
            aliases=['Region', 'Total number', 'Total duration'],
            sticky=False
        )
    ).add_to(map)

    _, col111, _ = st.columns([1,4,1])
    with col111:
        st_map = st_folium(map, width=1100)


# Displaying total number of Alerts by region horizontal barplot
with st.container(): 
    max_alerts_string = f"On {max_alerts.name[1].strftime('%Y-%m-%d')}, \
                        there were {max_alerts.duration['count']} Air Alerts issued in the {max_alerts.name[0]}, \
                        for a total duration of {max_alerts.duration['sum'].seconds//3600} hours \
                        and {(max_alerts.duration['sum'].seconds//60)%60} minutes"
    st.markdown(f"<h3 style='text-align: center; color: #8c785d;'>{max_alerts_string}</h1>", unsafe_allow_html=True)

    title_text = f'Total number of Alerts <br>(from {min_date} to {max_date})'   
    st.plotly_chart(create_barplot(total_alerts_by_region_df['count'], 
                                   total_alerts_by_region_df['region'],
                                   title_text), use_container_width=True, config=config_static)

# Displaying total duration of Alerts by region horizontal barplot
with st.container():
    longest_alert_string = f'The longest Air Alert (excluding Luhansk Oblast) started in the {longest_alert.region}, \
                            {longest_alert.started_at.date().strftime("%Y-%m-%d")} \
                            and lasted {longest_alert.duration.days} days, \
                            {longest_alert.duration.seconds//3600} hours \
                            and {(longest_alert.duration.seconds//60)%60} minutes'

    st.markdown(f"<h3 style='text-align: center; color: #8c785d;'>{longest_alert_string}</h1>", unsafe_allow_html=True)
    st.plotly_chart(create_barplot((total_duration_seconds_by_region_df['duration_seconds']/3600).round(2), 
                                    total_duration_seconds_by_region_df['region'],
                                    'Total duration of Alerts, hours'), use_container_width=True, config=config_static)
# Displaying Alerts issue part of the day distribution barpot
with st.container():
    max_period_percentage = round(max(periods_total_df['count'])/sum(periods_total_df['count'])*100)
    max_period_percantage_label = periods_total_df.iloc[periods_total_df['count'].argmax()]['start_period']
    max_period_percentage_string = f'Almost {max_period_percentage}% of Alerts issued was in the {max_period_percantage_label}'
    st.markdown(f"<h3 style='text-align: center; color: #8c785d;'>{max_period_percentage_string}</h1>", unsafe_allow_html=True)
    st.plotly_chart(create_barplot2(periods_total_df['start_period'], 
                                    periods_total_df['count'], 
                                    'Alerts issued by part of the day'), use_container_width=True, config=config_static)

# Displaying Alerts issue part of the day grouped by region horizontal barplot
with st.container():
    st.plotly_chart(create_barplot3(periods_grouped, 'count', 'region', 'start_period', 
                                    'Alerts issued by part of the day<br>(grouped by region)'), use_container_width=True)

st.markdown(
    '''
    Also check out [russian militry loses dashboard](https://kulturkamp-2022-war-loses-dashboa-russia-loses-dashboard-7k2mid.streamlit.app/)
    '''
)
# Displaying Data sources and Annotations sections                                
with st.container():
    col511, _ = st.columns([2, 3])
    with col511:
        with st.expander('Data sources'):
            st.markdown(
                '''
                - [Ukrainian air raid sirens dataset](https://github.com/Vadimkin/ukrainian-air-raid-sirens-dataset/tree/main/datasets) (csv, updated daily)
                - [First-level Administrative Divisions, Ukraine](https://geodata.lib.utexas.edu/catalog/stanford-gg870xt4706) (geoJSON)
                '''
            )

    col521, _ = st.columns([2, 3])
    with col521:
        with st.expander('Annotations'):
            st.markdown(
                '''
                1: Air Alert in the Luhansk Oblast was issued on 2022-04-04 the last time, and it is ongoing since then.
                '''
            )                                   