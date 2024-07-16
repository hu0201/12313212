import requests
import pandas as pd
from geopy.distance import distance
import folium
import os

def get_nearby_stations(user_lat, user_lon, max_distance=1000):
    url = "https://data.tycg.gov.tw/api/v1/rest/datastore/a1b4714b-3b75-4ff8-a8f2-cc377e4eaa0f?format=json&limit=287"
    response = requests.get(url)
    data = response.json()
    all_records = data['result']['records']
    df = pd.DataFrame(all_records)
    df['lat'] = df['lat'].astype(float)
    df['lng'] = df['lng'].astype(float)
    df['distance'] = df.apply(lambda row: distance((user_lat, user_lon), (row['lat'], row['lng'])).meters, axis=1)
    nearby_stations = df[df['distance'] < max_distance].sort_values(by='distance')
    top_five_stations = nearby_stations.head(5)
    top_five_stations['google_maps_link'] = top_five_stations.apply(
        lambda row: f"https://www.google.com/maps/search/?api=1&query={row['lat']},{row['lng']}",
        axis=1
    )
    # print(top_five_stations)
    return top_five_stations

def generate_map(user_lat, user_lon, top_five_stations, user_id):
    print('繪製地圖中...')
    m = folium.Map(location=[user_lat, user_lon], zoom_start=15)
    
    folium.Marker(
        location=[user_lat, user_lon],
        popup="Your Location",
        icon=folium.Icon(color='blue')
    ).add_to(m)

    for _, row in top_five_stations.iterrows():
        folium.Marker(
            location=[row['lat'], row['lng']],
            popup=f"{row['sna']}<br>Distance: {row['distance']:.2f} m<br>Total bikes: {row['tot']}<br>Available bikes: {row['sbi']}<br><a href='{row['google_maps_link']}' target='_blank'>Google Maps</a>",
            icon=folium.Icon(color='red')
        ).add_to(m)

    # 确保static目录存在于项目的根目录下
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    # 使用用户ID生成唯一文件名
    unique_filename = f"map_{user_id}.html"
    map_path = os.path.join(static_dir, unique_filename)
    m.save(map_path)
    return unique_filename