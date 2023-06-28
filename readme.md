# FIRMS Data Visualization

[![Pyhthon Version](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/release/python-370/)
[![Streamlit Version](https://img.shields.io/badge/streamlit-1.23.1-blue)](https://docs.streamlit.io/en/stable/)
[![GPLv3 License](https://img.shields.io/github/license/hcy2206/FIRMS_Data_Visualization)](https://opensource.org/licenses/GPL-3.0)
[![NASA](https://img.shields.io/badge/Data%20Source-NASA%20FIRMS-red)](https://firms.modaps.eosdis.nasa.gov/)

## Introduction
In this project, I have used the FIRMS data to create a visualization of the fire incidents that have occurred. It provides a lot of dimensions to filter the data. You can choose different countries and different days to see the fire incidents. You can also choose different satellite instruments to see the fire incidents. 

## Data Source
This project is based on [Fire Information for Resource Management System (FIRMS)](https://firms.modaps.eosdis.nasa.gov) data from NASA. The data is collected from the [MODIS](https://modis.gsfc.nasa.gov/), [VIIRS](https://www.nesdis.noaa.gov/current-satellite-missions/currently-flying/joint-polar-satellite-system/visible-infrared-imaging) and [LANDSAT](https://landsat.gsfc.nasa.gov) satellite instruments. The archive data is available for download from the [FIRMS website](https://firms.modaps.eosdis.nasa.gov/download/). Specifically, this project uses [APIs](https://firms.modaps.eosdis.nasa.gov/api/) provided by FIRMS to download the data in the real time.

## How to use
Download the python code, make sure you have installed the package `streamlit` and everyone imported on the top of the `main.py` file. Then run the code by `streamlit run main.py`, you will see the visualization in your browser.

Later I will create a requirement file to make it easier to install the packages.