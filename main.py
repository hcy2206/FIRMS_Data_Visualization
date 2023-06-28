import os
import streamlit as st
import pandas as pd
import requests
from io import StringIO
import plotly.express as px


def install_requirements():
    os.system('pip install -r requirements.txt')


# For Online Deployment
install_requirements()


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
def get_data_by_countries(countries, source, date_range, date, mapkey):
    mode = 'country'
    data_collect = pd.DataFrame()
    for country in countries:
        url = "https://firms.modaps.eosdis.nasa.gov/api/" + mode + "/csv/" + str(mapkey) + "/" + str(
            source) + "/" + str(
            country) + "/" + str(date_range) + "/" + str(date)
        data = get_data(url)
        data_collect = pd.concat([data_collect, data], ignore_index=True)
    # 如果<html>列有值，则删除该行
    if '<html>' in data_collect.columns:
        data_collect = data_collect[data_collect['<html>'].isnull()]
    return data_collect


@st.cache_data
def date_lines(data):
    if 'acq_date' in data.columns:
        date_count = data.groupby('acq_date').size().reset_index(name='count')
        if date_count['acq_date'].nunique() == 1:
            return False
        date_line = px.line(date_count, x='acq_date', y='count')
        date_line.update_layout(xaxis_title='Date', yaxis_title='Count')
        return date_line
    else:
        return False


@st.cache_data
def country_lines(data):
    if 'country_id' not in data.columns:
        return False
    country_count = data.groupby('country_id').size().reset_index(name='count')
    country_count['country'] = country_count['country_id'].apply(lambda x: st.session_state.countries_dict[x])
    if country_count['country'].nunique() == 1:
        return False
    # country_bar_polar = px.bar_polar(country_count)
    # country_bar_polar.update_layout(xaxis_title='Country', yaxis_title='Count')
    # return country_bar_polar
    country_bar = px.bar(country_count, x='country', y='count')
    country_bar.update_layout(xaxis_title='Country', yaxis_title='Count')
    return country_bar


@st.cache_data
def local_get_data(source, year, country):
    year = str(year)
    country = country.replace(' ', '_')
    country = country.replace("'", '_')
    address = source + "/" + year + "/" + source + "_" + year + "_" + country + ".csv"
    try:
        data = pd.read_csv(address)
        data['country'] = country
    except FileNotFoundError:
        data = pd.read_csv('modis/modis_empty.csv')
        data['country'] = ''
    return data


@st.cache_data
def check_date(begin_year, end_year):
    if begin_year > end_year:
        st.error('Begin year should be earlier than end year!')
        return False
    else:
        return True


@st.cache_data
def data_collection(year_begin, year_end, country_multi):
    data = pd.read_csv('modis/modis_empty.csv')
    data['country'] = ''
    for country in country_multi:
        for year in range(year_begin, year_end + 1):
            data = pd.concat([data, local_get_data('modis', year, country)], ignore_index=True)
    return data


@st.cache_data
def count_by_date_seprate_by_country_line(data):
    data = data.groupby(['acq_date', 'country']).size().reset_index(name='count')
    date_line = px.line(data, x='acq_date', y='count', color='country')
    date_line.update_layout(xaxis_title='Date', yaxis_title='Count')
    return date_line


# Page Configuration
st.set_page_config(page_title="FIRMS Data Visualization",
                   page_icon="https://markdown-tuchuang-hcy2206.oss-cn-shanghai.aliyuncs.com/img/202306151943857.png",
                   initial_sidebar_state="auto",
                   menu_items={"About": "This is a world wide fire events data visualization project based "
                                        "on Streamlit by Python, data provided by NASA FIRMS.\n \n"
                                        "Github Repositorie [hcy2206/FIRMS_Data_Visualization]("
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

"## Fire Information for Resource Management System"
"# Worldwide Fire Data Visualization"

# Sidebar
with st.sidebar:
    st.write('## Data Selection')
    online = st.selectbox(label='Select the data source, **Online** or **Local**',
                          options=[True, False],
                          format_func=lambda x: 'Online' if x else 'Local',
                          index=0)
    if online:
        # world = st.checkbox(label='The Whole World', value=False, help='To get the data of the whole world')
        world = False
        if world:
            country_multi = st.session_state.countries['abreviation']
            st.warning('Warning! Data will be requested country by country, it would take a long time!')
        else:
            country_multi = st.multiselect(label='Country',
                                           options=st.session_state.countries['abreviation'],
                                           help='Please do not select too many countries at once, the api key is limited.',
                                           format_func=lambda x: st.session_state.countries_dict[x],
                                           default=['CHN', 'USA'])
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
    else:
        world = st.checkbox(label='The Whole World', value=False, help='To get the data of the whole world')
        if world:
            country_multi = st.session_state.countries['abreviation']
            st.warning('Warning! Data will be loaded country by country, it would take a long time!')
        else:
            country_multi = st.multiselect(label='Country',
                                           options=st.session_state.countries['name'],
                                           help='Please do not select too many countries at once, the api key is limited.',
                                           default=['China', 'United States'])
        source = st.selectbox(label='Source', options=['modis'], format_func=lambda x: 'MODIS(SP)')

        # time_scale = st.selectbox(label='Time Scale', options=['Year', 'Month', 'Day'], index=1)
        time_scale = 'Year'
        # 分为两列
        begin_left, end_right = st.columns(2)
        if time_scale == 'Day':
            date_begin = st.date_input(label='Begin Date',
                                       min_value=pd.to_datetime('2000-11-01'),
                                       max_value=pd.to_datetime('2022-12-31'),
                                       value=pd.to_datetime('2022-11-01'))
            date_end = st.date_input(label='End Date',
                                     value=pd.to_datetime('2022-12-31'),
                                     min_value=pd.to_datetime('2000-11-01'),
                                     max_value=pd.to_datetime('2022-12-31'))
        elif time_scale == 'Month':
            begin_left.write('**Begin Month**')
            end_right.write('**End Month**')
            year_begin = begin_left.selectbox(label='Year', options=list(range(2000, 2023)), index=20,
                                              key='year_begin')
            year_end = end_right.selectbox(label='Year', options=list(range(2000, 2023)), index=22, key='year_end')
            if year_begin == 2000:
                month_begin = begin_left.selectbox(label='Month', options=list(range(11, 13)), index=0,
                                                   key='month_begin')
            else:
                month_begin = begin_left.selectbox(label='Month', options=list(range(1, 13)), index=0,
                                                   key='month_begin')
            if year_end == 2000:
                month_end = end_right.selectbox(label='Month', options=list(range(11, 13)), index=0, key='month_end')
            else:
                month_end = end_right.selectbox(label='Month', options=list(range(1, 13)), index=11, key='month_end')
        elif time_scale == 'Year':
            year_begin = begin_left.selectbox(label='Begin Year', options=list(range(2000, 2023)), index=20,
                                              key='year_begin')
            year_end = end_right.selectbox(label='End Year', options=list(range(2000, 2023)), index=22, key='year_end')

        submit = st.button(label='Submit & Refresh', help='Click to get data')

# Main Page
if submit:
    if online:
        st.session_state.data = get_data_by_countries(country_multi, source, date_range, date, mapkey)
        if not world:
            st.session_state.country_display = ',%20'.join(
                list(
                    map(
                        lambda x: st.session_state.countries_dict[x].replace(' ', '%20'), country_multi
                    )
                )
            )
        else:
            st.session_state.country_display = 'World'
        st.session_state.date_display = str(date).replace('-', '--')
        st.session_state.source_display = st.session_state.source_dict[source].replace(' ', '%20')
        st.session_state.date_range_display = str(date_range) + '%20days'
    else:
        if check_date(begin_year=year_begin, end_year=year_end):
            st.session_state.data = data_collection(year_begin=year_begin,
                                                    year_end=year_end,
                                                    country_multi=country_multi)
# main-map
if online:
    st.write('![](https://img.shields.io/badge/Country-' + st.session_state.country_display + '-blue)',
             '![](https://img.shields.io/badge/Date-' + st.session_state.date_display + '-brightgreen)',
             '![](https://img.shields.io/badge/Date%20Range-' + st.session_state.date_range_display + '-yellow)')
    st.map(st.session_state.data)
else:
    country_badge_list = []
    for name in country_multi:
        country_badge_list.append(name.replace(' ', '%20'))
    st.write('![](https://img.shields.io/badge/Years-' + str(year_begin) + '--' + str(year_end) + '-brightgreen)',
             '![](https://img.shields.io/badge/Countries-' + ',%20'.join(country_badge_list) + '-blue)')
    st.map(st.session_state.data)

# main-date
if online:
    date_line = date_lines(st.session_state.data)
    if date_line:
        st.write("### Count by Date")
        st.write('![](https://img.shields.io/badge/Country-' + st.session_state.country_display + '-blue)')
        st.plotly_chart(date_line)
else:
    date_line = date_lines(st.session_state.data)
    if date_line:
        st.write("### Count by Date")
        # badge_list = []
        # for name in country_multi:
        #     name = name.replace(' ', '%20')
        #     badge_list.append('![](https://img.shields.io/badge/Country-' + name + '-blue)')
        # st.write(' '.join(badge_list))
        # st.plotly_chart(date_line)
        st.plotly_chart(count_by_date_seprate_by_country_line(st.session_state.data))


# main-country
country_lines = country_lines(st.session_state.data)
if country_lines:
    st.write("### Count by Country")
    st.write('![](https://img.shields.io/badge/Date-' + st.session_state.date_display + '-brightgreen)',
             '![](https://img.shields.io/badge/Date%20Range-' + st.session_state.date_range_display + '-yellow)')
    st.plotly_chart(country_lines)

# main-country-local
if not online and len(country_multi) >= 2:
    country_count = st.session_state.data.groupby('country').size().reset_index(name='count')
    country_lines = px.bar(country_count, x='country', y='count')
    country_lines.update_layout(xaxis_title='Country', yaxis_title='Count')
    st.write("### Count by Country")
    st.write('![](https://img.shields.io/badge/Years-' + str(year_begin) + '--' + str(year_end) + '-brightgreen)')
    st.plotly_chart(country_lines)


# Original Data
origin_data = st.checkbox(label='Show Original Data', value=False)
if origin_data:
    st.write("### Original Data")
    if online:
        st.write('![](https://img.shields.io/badge/Instrument-' + st.session_state.source_display + '-yellowgreen)')
    else:
        st.write('![](https://img.shields.io/badge/Instrument-MODIS-yellowgreen)')
    st.write(st.session_state.data)
    st.write("[Attribute table for LANDSAT](https://www.earthdata.nasa.gov/faq/firms-faq#ed-landsat-fires-attributes)")
    st.write("[Attribute table for MODIS](https://go.nasa.gov/3JSgbdb)")
    st.write("[Attribute table for VIIRS](https://go.nasa.gov/3sf3ALb)")

