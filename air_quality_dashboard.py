
import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
import time
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="🌍 Global Air Quality Dashboard",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .aqi-good { color: #00E400; font-weight: bold; }
    .aqi-moderate { color: #FFFF00; font-weight: bold; }
    .aqi-unhealthy { color: #FF0000; font-weight: bold; }
    .aqi-very-unhealthy { color: #8F3F97; font-weight: bold; }
    .aqi-hazardous { color: #7E0023; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Helper functions (copied from notebook)
def calculate_aqi(pm25_value):
    """Calculate Air Quality Index (AQI) from PM2.5 values"""
    if pd.isna(pm25_value):
        return None
    
    if pm25_value <= 12:
        return int(((50 - 0) / (12 - 0)) * pm25_value + 0)
    elif pm25_value <= 35.4:
        return int(((100 - 51) / (35.4 - 12.1)) * (pm25_value - 12.1) + 51)
    elif pm25_value <= 55.4:
        return int(((150 - 101) / (55.4 - 35.5)) * (pm25_value - 35.5) + 101)
    elif pm25_value <= 150.4:
        return int(((200 - 151) / (150.4 - 55.5)) * (pm25_value - 55.5) + 151)
    elif pm25_value <= 250.4:
        return int(((300 - 201) / (250.4 - 150.5)) * (pm25_value - 150.5) + 201)
    else:
        return int(((400 - 301) / (350.4 - 250.5)) * (pm25_value - 250.5) + 301)

def get_aqi_category(aqi):
    """Get AQI category and color"""
    if pd.isna(aqi):
        return "No Data", "#CCCCCC"
    elif aqi <= 50:
        return "Good", "#00E400"
    elif aqi <= 100:
        return "Moderate", "#FFFF00"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "#FF7E00"
    elif aqi <= 200:
        return "Unhealthy", "#FF0000"
    elif aqi <= 300:
        return "Very Unhealthy", "#8F3F97"
    else:
        return "Hazardous", "#7E0023"

def get_health_recommendation(aqi):
    """Get health recommendations based on AQI"""
    if pd.isna(aqi):
        return "No data available"
    elif aqi <= 50:
        return "🟢 Great day for outdoor activities!"
    elif aqi <= 100:
        return "🟡 Generally safe, but sensitive people should consider reducing prolonged outdoor exertion"
    elif aqi <= 150:
        return "🟠 Sensitive groups should reduce outdoor activities"
    elif aqi <= 200:
        return "🔴 Everyone should limit outdoor activities"
    elif aqi <= 300:
        return "🟣 Avoid outdoor activities - health alert!"
    else:
        return "⚫ Emergency conditions - stay indoors!"

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def fetch_city_air_quality(city_name, api_token="demo"):
    """Fetch air quality data for a specific city from WAQI API"""
    base_url = "https://api.waqi.info/feed"
    url = f"{base_url}/{city_name}/?token={api_token}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'ok':
            return data.get('data')
        else:
            return None
    except:
        return None

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def fetch_multiple_cities_data(cities_list, api_token="demo"):
    """Fetch air quality data for multiple cities"""
    all_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, city in enumerate(cities_list):
        status_text.text(f'Fetching data for {city}...')
        progress_bar.progress((i + 1) / len(cities_list))
        
        city_data = fetch_city_air_quality(city, api_token)
        if city_data:
            city_data['query_city'] = city
            all_data.append(city_data)
        
        time.sleep(0.3)  # Be respectful to the API
    
    status_text.text('Data collection complete!')
    time.sleep(1)
    status_text.empty()
    progress_bar.empty()
    
    return all_data

def waqi_data_to_dataframe(waqi_data_list):
    """Convert WAQI API data to pandas DataFrame"""
    if not waqi_data_list:
        return pd.DataFrame()
    
    data_list = []
    
    for city_data in waqi_data_list:
        base_info = {
            'city': city_data.get('city', {}).get('name', 'Unknown'),
            'query_city': city_data.get('query_city', 'Unknown'),
            'aqi': city_data.get('aqi', None),
            'latitude': None,
            'longitude': None,
            'date': city_data.get('time', {}).get('s', None),
            'url': city_data.get('city', {}).get('url', None)
        }
        
        geo = city_data.get('city', {}).get('geo', [])
        if len(geo) >= 2:
            base_info['latitude'] = float(geo[0]) if geo[0] else None
            base_info['longitude'] = float(geo[1]) if geo[1] else None
        
        iaqi = city_data.get('iaqi', {})
        
        pollutants_found = False
        for pollutant, data in iaqi.items():
            if isinstance(data, dict) and 'v' in data:
                pollutants_found = True
                row = base_info.copy()
                row.update({
                    'parameter': pollutant,
                    'value': data['v'],
                    'unit': 'AQI'
                })
                data_list.append(row)
        
        if not pollutants_found and base_info['aqi'] is not None:
            row = base_info.copy()
            row.update({
                'parameter': 'overall_aqi',
                'value': base_info['aqi'],
                'unit': 'AQI'
            })
            data_list.append(row)
    
    if not data_list:
        return pd.DataFrame()
    
    df = pd.DataFrame(data_list)
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df['aqi_category'] = df['aqi'].apply(lambda x: get_aqi_category(x)[0] if pd.notna(x) else 'No Data')
        df['health_recommendation'] = df['aqi'].apply(lambda x: get_health_recommendation(x) if pd.notna(x) else 'No data available')
        df['country'] = df['city'].apply(lambda x: x.split(',')[-1].strip() if ',' in str(x) else 'Unknown')
    
    return df

def create_world_map(df):
    """Create interactive world map"""
    if df.empty:
        return None
    
    aqi_data = df[
        (df['parameter'] == 'overall_aqi') & 
        (df['latitude'].notna()) & 
        (df['longitude'].notna()) &
        (df['aqi'].notna())
    ].copy()
    
    if aqi_data.empty:
        return None
    
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    for idx, row in aqi_data.iterrows():
        category, color = get_aqi_category(row['aqi'])
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=8,
            popup=f"{row['city']}<br>AQI: {row['aqi']}<br>{category}",
            color='black',
            weight=1,
            fillColor=color,
            fillOpacity=0.7
        ).add_to(m)
    
    return m

def main():
    # Header
    st.markdown('<h1 class="main-header">🌍 Global Air Quality Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("**Real-time air quality data from cities worldwide**")
    
    # Sidebar
    st.sidebar.header("🎛️ Dashboard Controls")
    
    # API Token input
    api_token = st.sidebar.text_input(
        "🔑 WAQI API Token", 
        value="demo", 
        help="Get your free token at aqicn.org/data-platform/token/"
    )
    
    # City selection
    default_cities = [
        'london', 'paris', 'berlin', 'new york', 'los angeles', 'beijing', 
        'tokyo', 'mumbai', 'delhi', 'sydney', 'moscow', 'cairo'
    ]
    
    selected_cities = st.sidebar.multiselect(
        "🏙️ Select Cities",
        options=[
            'london', 'paris', 'berlin', 'madrid', 'rome', 'amsterdam',
            'new york', 'los angeles', 'chicago', 'toronto', 'mexico city',
            'beijing', 'shanghai', 'tokyo', 'seoul', 'mumbai', 'delhi', 'bangkok',
            'sydney', 'melbourne', 'moscow', 'istanbul', 'dubai', 'cairo',
            'sao paulo', 'rio de janeiro', 'buenos aires', 'santiago'
        ],
        default=default_cities[:8]
    )
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
    
    # Load data
    if selected_cities:
        with st.spinner('Fetching real-time air quality data...'):
            raw_data = fetch_multiple_cities_data(selected_cities, api_token)
            df = waqi_data_to_dataframe(raw_data)
        
        if not df.empty:
            # Summary metrics
            aqi_data = df[df['parameter'] == 'overall_aqi']
            
            if not aqi_data.empty:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("🏙️ Cities Monitored", len(aqi_data))
                
                with col2:
                    avg_aqi = aqi_data['aqi'].mean()
                    st.metric("📊 Average AQI", f"{avg_aqi:.0f}")
                
                with col3:
                    best_city = aqi_data.loc[aqi_data['aqi'].idxmin()]
                    st.metric("🟢 Best Air Quality", f"{best_city['city']} ({best_city['aqi']:.0f})")
                
                with col4:
                    worst_city = aqi_data.loc[aqi_data['aqi'].idxmax()]
                    st.metric("🔴 Worst Air Quality", f"{worst_city['city']} ({worst_city['aqi']:.0f})")
            
            # Main content tabs
            tab1, tab2, tab3 = st.tabs(["🗺️ World Map", "📊 City Rankings", "📈 Analysis"])
            
            with tab1:
                st.subheader("🗺️ Global Air Quality Map")
                world_map = create_world_map(df)
                if world_map:
                    map_data = st_folium(world_map, width=1200, height=500)
            
            with tab2:
                st.subheader("📊 City Air Quality Rankings")
                
                if not aqi_data.empty:
                    # Create ranking chart
                    aqi_sorted = aqi_data.sort_values('aqi', ascending=False)
                    
                    fig = px.bar(
                        aqi_sorted,
                        x='aqi',
                        y='city',
                        orientation='h',
                        title='Cities Ranked by Air Quality Index (Worst First)',
                        color='aqi_category',
                        color_discrete_map={
                            'Good': '#00E400',
                            'Moderate': '#FFFF00',
                            'Unhealthy for Sensitive Groups': '#FF7E00',
                            'Unhealthy': '#FF0000',
                            'Very Unhealthy': '#8F3F97',
                            'Hazardous': '#7E0023'
                        }
                    )
                    fig.update_layout(height=600, yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # City details table
                    st.subheader("📋 Detailed City Information")
                    display_df = aqi_data[['city', 'aqi', 'aqi_category', 'health_recommendation']].copy()
                    display_df.columns = ['City', 'AQI', 'Category', 'Health Recommendation']
                    st.dataframe(display_df, use_container_width=True)
            
            with tab3:
                st.subheader("📈 Air Quality Analysis")
                
                if not aqi_data.empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # AQI distribution
                        fig_hist = px.histogram(
                            aqi_data, 
                            x='aqi', 
                            nbins=15,
                            title='Distribution of AQI Values'
                        )
                        st.plotly_chart(fig_hist, use_container_width=True)
                    
                    with col2:
                        # Category pie chart
                        category_counts = aqi_data['aqi_category'].value_counts()
                        fig_pie = px.pie(
                            values=category_counts.values,
                            names=category_counts.index,
                            title='Air Quality Categories Distribution'
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    # Pollutant comparison
                    st.subheader("🔬 Pollutant Levels Comparison")
                    pollutant_data = df[df['parameter'].isin(['pm25', 'pm10', 'no2', 'so2', 'co', 'o3'])]
                    
                    if not pollutant_data.empty:
                        fig_pollutants = px.bar(
                            pollutant_data,
                            x='city',
                            y='value',
                            color='parameter',
                            title='Pollutant Levels by City',
                            barmode='group'
                        )
                        fig_pollutants.update_layout(xaxis_tickangle=-45)
                        st.plotly_chart(fig_pollutants, use_container_width=True)
        
        else:
            st.error("No data available. Please check your internet connection or try different cities.")
    
    else:
        st.info("👆 Please select cities from the sidebar to view air quality data.")
    
    # Footer
    st.markdown("---")
    st.markdown("**Data Source:** [World Air Quality Index](https://waqi.info/) | **Built with:** Streamlit & Python")
    st.markdown("**Note:** Air quality data is updated in real-time from monitoring stations worldwide.")

if __name__ == "__main__":
    main()
