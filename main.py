import streamlit as st
import pandas as pd
import requests
from io import StringIO
import plotly.express as px

from geolib import get_country_baiduapi


@st.cache_data
def get_data(data_url):
    data_response = requests.get(data_url)
    data_result = pd.read_csv(StringIO(data_response.content.decode('utf-8')))
    return data_result


@st.cache_data
def date_available(mapkey, source):
    data_url = "https://firms.modaps.eosdis.nasa.gov/api/data_availability/csv/" \
               + str(mapkey) + "/" + str(source)
    data_response = requests.get(data_url).content.decode('utf-8')
    lst = data_response.split('\n')
    keys = lst[0].split(',')
    values = lst[1].split(',')
    data_available = dict(zip(keys, values))
    return data_available


@st.cache_data
def countries_name():
    countries = requests.get('https://firms.modaps.eosdis.nasa.gov/api/countries').content.decode('utf-8')
    # countries是用;分隔的字符串，需要转换成dataframe
    countries_df = pd.read_csv(StringIO(countries), sep=';')
    return countries_df


@st.cache_data
def date_lines(data):
    if 'acq_date' in data.columns:
        date_count = data.groupby('acq_date').size().reset_index(name='count')
        if date_count['acq_date'].nunique() == 1:
            return False
        date_bar = px.line(date_count, x='acq_date', y='count')
        date_bar.update_layout(xaxis_title='Date', yaxis_title='Count')
        return date_bar
    else:
        return False


@st.cache_data
def country_lines(data):
    if 'latitude' in data.columns and 'longitude' in data.columns:
        data['country'] = data.apply(lambda x: get_country_baiduapi(x['latitude'],x['longitude']),axis=1)
        country_count = data.groupby('country').size().reset_index(name='count')
        country_bar = px.line(country_count, x='country', y='count')
        country_bar.update_layout(xaxis_title='Country', yaxis_title='Count')
        return country_bar
    else:
        return False


# Page Configuration
st.set_page_config(page_title="FIRMS Data Visualization",
                   page_icon="https://markdown-tuchuang-hcy2206.oss-cn-shanghai.aliyuncs.com/img/202306151943857.png",
                   initial_sidebar_state="auto",
                   menu_items={"About": "Github  Repositorie [hcy2206/FIRMS_Data_Visualization]("
                                        "https://github.com/hcy2206/FIRMS_Data_Visualization.git)"},
                   layout="wide")

# Session State Initialization (cache, only run once, it won't be refreshed)
if 'source' not in st.session_state:
    st.session_state.source = ['LANDSAT_NRT', 'MODIS_NRT', 'MODIS_SP', 'VIIRS_NOAA20_NRT', 'VIIRS_SNPP_NRT',
                               'VIIRS_SNPP_SP']
if 'source_dict' not in st.session_state:
    st.session_state.source_dict = {'LANDSAT_NRT': 'LANDSAT (NRT) [US/Canada only]',
                                    'MODIS_NRT': 'MODIS (URT+NRT)',
                                    'MODIS_SP': 'MODIS(SP)',
                                    'VIIRS_NOAA20_NRT': 'VIIRS NOAA-20(URT+NRT)',
                                    'VIIRS_SNPP_NRT': 'VIIRS S-NPP(URT+NRT)',
                                    'VIIRS_SNPP_SP': 'VIIRS S-NPP(SP)'}
if 'countries' not in st.session_state:
    st.session_state.countries = countries_name().sort_values(by='name').reset_index(drop=True)
if 'countries_dict' not in st.session_state:
    st.session_state.countries_dict = dict(zip(st.session_state.countries['abreviation'],
                                               st.session_state.countries['name']))
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame()
if 'country_display' not in st.session_state:
    st.session_state.country_display = ''
if 'date_display' not in st.session_state:
    st.session_state.date_display = ''
if 'source_display' not in st.session_state:
    st.session_state.source_display = ''
if 'date_range_display' not in st.session_state:
    st.session_state.date_range_display = ''

"## Fire Information for Resource Management System (FIRMS)"
"# Worldwide Fire Data Visualization"

# Sidebar
with st.sidebar:
    country = 'world'
    st.write('## Data Selection')
    world = st.checkbox(label='The Whole World', value=False, help='To get the data of the whole world')
    if world:
        pass
    else:
        country = st.selectbox(label='Country', options=st.session_state.countries['abreviation'],
                               format_func=lambda x: st.session_state.countries_dict[x], index=231)
    source = st.selectbox(label='Source', options=st.session_state.source, index=2,
                          format_func=lambda x: st.session_state.source_dict[x])
    date_container = st.container()
    date_range = st.slider(label='Date Range', min_value=1, max_value=10, value=1, step=1, format='%d days',
                           help='Begin from the date selected above')
    submit = st.button(label='Submit & Refresh', help='Click to get data')
    mapkey = st.text_input(label='FIRMS MAP_KEY', value='5adc6cf4c673ab710edc696e0039e713')
    check_mapkey = st.button(label='Check MAP_KEY Status', help='Click to check your MAP_KEY status')
    if check_mapkey:
        url_check = "https://firms.modaps.eosdis.nasa.gov/mapserver/mapkey_status/?MAP_KEY=" + str(mapkey)
        response = requests.get(url_check)
        if response.content == b'MAP_KEY is invalid or your have exceeded your transaction/time limit. Please try ' \
                               b'again later.':
            st.error('**Invalid MAP_KEY**')
        else:
            mapkey_status_json = response.json()
            st.write(mapkey_status_json['current_transactions'], '/', mapkey_status_json['transaction_limit'],
                     'in the past ', mapkey_status_json['transaction_interval'])
    st.markdown('<a href="https://firms.modaps.eosdis.nasa.gov/api/area/#mapKey">Apply FIRMS MAP_KEY for Free</a>',
                unsafe_allow_html=True)
    date_available = date_available(mapkey, source)
    date = date_container.date_input(label='Date', value=pd.to_datetime(str(date_available['max_date'])),
                                     min_value=pd.to_datetime(str(date_available['min_date'])),
                                     max_value=pd.to_datetime(str(date_available['max_date'])))
    if world:
        mode = 'area'
        country = 'world'
    else:
        mode = 'country'
    url = "https://firms.modaps.eosdis.nasa.gov/api/" + mode + "/csv/" + str(mapkey) + "/" + str(
        source) + "/" + str(
        country) + "/" + str(date_range) + "/" + str(date)

# Main Page
if submit:
    st.session_state.data = get_data(url)
    if not world:
        st.session_state.country_display = st.session_state.countries_dict[country].replace(' ', '%20')
    else:
        st.session_state.country_display = 'World'
    st.session_state.date_display = str(date).replace('-', '--')
    st.session_state.source_display = st.session_state.source_dict[source].replace(' ', '%20')
    st.session_state.date_range_display = str(date_range) + '%20days'

# main-map
st.write('![](https://img.shields.io/badge/Country-' + st.session_state.country_display + '-blue)',
         '![](https://img.shields.io/badge/Date-' + st.session_state.date_display + '-brightgreen)',
         '![](https://img.shields.io/badge/Date%20Range-' + st.session_state.date_range_display + '-yellow)')
st.map(st.session_state.data)

# main-date
date_line = date_lines(st.session_state.data)
if date_line:
    st.write("### Count by Date")
    st.write('![](https://img.shields.io/badge/Country-' + st.session_state.country_display + '-blue)')
    st.plotly_chart(date_line)

# mian-country
if world:
    country_lines = country_lines(st.session_state.data)
    if country_lines:
        st.write("### Count by Country")
        st.write('![](https://img.shields.io/badge/Date-' + st.session_state.date_display + '-brightgreen)')
        st.plotly_chart(country_lines)

# Original Data
origin_data = st.checkbox(label='Show Original Data', value=False)
if origin_data:
    st.write("### Original Data")
    st.write('![](https://img.shields.io/badge/Satellite-' + st.session_state.source_display + '-yellowgreen)')
    st.write(st.session_state.data)
    st.write("[Attribute table for LANDSAT](https://www.earthdata.nasa.gov/faq/firms-faq#ed-landsat-fires-attributes)")
    st.write("[Attribute table for MODIS](https://go.nasa.gov/3JSgbdb)")
    st.write("[Attribute table for VIIRS](https://go.nasa.gov/3sf3ALb)")

# debug mode
debug = st.checkbox(label='Debug Mode', value=False)
debug_container = st.container()
if debug:
    debug_container.write("## Debug Mode")
    debug_container.write("Data:")
    debug_container.write(st.session_state.data)
    debug_container.write(st.session_state.countries_dict[country])
    debug_container.write(country)
    # debug_container.write(st.session_state.countries_dict)
    debug_container.write(st.session_state.countries_dict['ATF'].replace(' ', '%20'))
    debug_container.write(date_lines(st.session_state.data))
    debug_container.plotly_chart(date_lines(st.session_state.data))
