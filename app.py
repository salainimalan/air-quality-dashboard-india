import os
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="Air Quality Analytics & Visualization Dashboard - India",
    layout="wide"
)

# ---- Centered Layout ----
with st.container():
    left_space, main_col, right_space = st.columns([0, 0.7, 0])  # Center alignment
    with main_col:
        st.markdown(
            "<h1 style='text-align:center; font-weight:800;'>Air Quality Analytics & Visualization Dashboard - India</h1>",
            unsafe_allow_html=True,
        )

        st.info("""
        The **Air Quality Prediction & Visualization** project is an end-to-end **Big Data analytics platform**
        built using **Apache Spark**, **Plotly**, and **Streamlit**.  
        It enables interactive exploration of pollution levels, identifies regional air quality trends,
        and presents findings through a visually engaging dashboard.  
       .
        """)

       
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("###  Data Sources")
            st.markdown("""
            The dataset integrates information from multiple **air quality monitoring sensors** across India:

            - **City & Location** identifiers  
            - **Timestamped readings** for accurate trend analysis  
            - Concentrations of **PM2.5, PM10, NO₂, SO₂, CO**, and **O₃**  
            - Calculated **Air Quality Index (AQI)** values  
            - Cleaned and aggregated using **PySpark** for scalable analysis  
            """)

        with col2:
            st.markdown("###  Dashboard Features")
            st.markdown("""
            - **City-wise Pollutant Averages:** Compare pollution intensity across regions  
            - **Interactive Map:** Explore real-time spatial AQI variations  
            - **Data Volume Overview:** Check the number of records per city  
            - **Trends & Patterns:** Visualize pollutant dominance and seasonal shifts  
            - **Spark Integration:** Efficient large-scale data processing via **Spark SQL**  
            """)

        st.markdown("---")




df = pd.read_csv("combined.csv")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Records & Sensors", "Maps", "City Pollutant Levels",
    "Monthly Trends", "Hourly Trends", "Correlation Heatmap",
    "Pollutant Composition"
])


with tab1:
    city_counts = df.groupby("city").size().reset_index(name="record_count").sort_values(by="record_count", ascending=False)
    fig1 = px.bar(city_counts, x='city', y='record_count', title='Total Records per City', text='record_count',
                  color='record_count', color_continuous_scale='viridis')
    st.plotly_chart(fig1, use_container_width=True)

    sensor_summary = df.groupby("city")["location_id"].nunique().reset_index(name="unique_sensors").sort_values("unique_sensors", ascending=False)
    fig3 = px.bar(sensor_summary, x="city", y="unique_sensors", title="Unique Sensors per City", text="unique_sensors",
                  color="unique_sensors", color_continuous_scale="viridis")
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    df_2025 = df.copy()
    sensor_locations = df_2025[['city', 'location_id', 'location_name', 'latitude', 'longitude']].drop_duplicates()
    cities = sensor_locations['city'].unique()
    for city in cities:
        city_data = sensor_locations[sensor_locations['city'] == city]
        fig = px.scatter_mapbox(
            city_data, lat='latitude', lon='longitude', color='city',
            hover_name='location_name',
            hover_data={'location_id': True, 'latitude': ':.3f', 'longitude': ':.3f'},
            title=f'Sensor Locations in {city} (2025)',
            zoom=10,
            center=dict(lat=city_data['latitude'].mean(), lon=city_data['longitude'].mean()),
            mapbox_style='carto-positron', height=550
        )
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    city_avg = df.groupby(['city', 'parameter'])['value'].mean().reset_index()
    pollutants = city_avg['parameter'].unique()
    for pollutant in pollutants:
        pollutant_data = city_avg[city_avg['parameter'] == pollutant].sort_values('value', ascending=False)
        fig = px.bar(pollutant_data, x='city', y='value', color='value', color_continuous_scale='viridis',
                     text='value', title=f'Average {pollutant.upper()} Levels by City (2016–2025)')
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    df['datetimeUtc'] = pd.to_datetime(df['datetimeUtc'], errors='coerce')
    df['month'] = df['datetimeUtc'].dt.month_name()
    monthly_avg = df.groupby(['parameter', 'city', 'month'], sort=False)['value'].mean().reset_index()
    month_order = ['January','February','March','April','May','June','July','August','September','October','November','December']
    monthly_avg['month'] = pd.Categorical(monthly_avg['month'], categories=month_order, ordered=True)
    city_colors = px.colors.qualitative.Set2
    for pollutant in monthly_avg['parameter'].unique():
        plot_data = monthly_avg[monthly_avg['parameter'] == pollutant].sort_values('month')
        fig = px.area(plot_data, x='month', y='value', color='city',
                      title=f"Monthly Average {pollutant.upper()} Levels Across Cities",
                      color_discrete_sequence=city_colors)
        st.plotly_chart(fig, use_container_width=True)


with tab5:
    if 'hour' not in df.columns:
        df['datetimeUtc'] = pd.to_datetime(df['datetimeUtc'], errors='coerce')
        df['hour'] = df['datetimeUtc'].dt.hour

    hourly_avg = df.groupby(['parameter', 'hour'])['value'].mean().reset_index()
    color_map = {"pm25": "#ff4500","pm10": "#ffa500","no2": "#1f77b4","so2": "#9467bd","o3": "#2ca02c","co": "#8c564b"}
    fig = px.area(hourly_avg, x='hour', y='value', color='parameter',
                  title="Average Hourly Pollutant Levels Across India",
                  color_discrete_map=color_map)
    st.plotly_chart(fig, use_container_width=True)

with tab6:
    pivot_df = df.groupby(['city', 'parameter'])['value'].mean().reset_index().pivot(index='city', columns='parameter', values='value')
    corr = pivot_df.corr()
    fig, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(corr, annot=True, cmap="inferno", fmt=".2f", linewidths=0.5,
                cbar_kws={'label': 'Correlation'}, square=True, ax=ax)
    st.pyplot(fig)

with tab7:
    pollutant_mix = df.groupby(['city', 'parameter'])['value'].mean().reset_index()
    for city_name, city_data in pollutant_mix.groupby('city'):
        fig = px.pie(city_data, names='parameter', values='value', color='parameter',
                     color_discrete_sequence=px.colors.sequential.Inferno, hole=0.4,
                     title=f'Pollutant Composition in {city_name}', height=500)
        st.plotly_chart(fig, use_container_width=True)
