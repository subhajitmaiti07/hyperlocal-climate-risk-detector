import folium
import os
from folium.plugins import MarkerCluster

OUTPUT_DIR = "outputs/maps"
MAP_FILE = "realtime_map.html"


def generate_map(lat, lon, weather=None, predictions=None):
    """
    Generate a production-ready interactive map.

    Args:
        lat (float): Latitude
        lon (float): Longitude
        weather (dict): Weather data
        predictions (dict): ML predictions
    """

    # =========================
    # VALIDATION
    # =========================
    if lat is None or lon is None:
        raise ValueError("Latitude and Longitude are required")

    # =========================
    # BASE MAP (SAFE TILE)
    # =========================
    m = folium.Map(
        location=[lat, lon],
        zoom_start=10,
        control_scale=True,
        tiles="OpenStreetMap"  # always safe
    )

    # =========================
    # EXTRA TILE LAYERS (WITH ATTRIBUTION)
    # =========================
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        attr="© OpenStreetMap © CARTO",
        name="Light"
    ).add_to(m)

    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        attr="© OpenStreetMap © CARTO",
        name="Dark"
    ).add_to(m)

    # =========================
    # MARKER CLUSTER (SCALABLE)
    # =========================
    marker_cluster = MarkerCluster().add_to(m)

    # =========================
    # SAFE DATA EXTRACTION
    # =========================
    temp = weather.get("temperature_C", "N/A") if weather else "N/A"
    humidity = weather.get("humidity_pct", "N/A") if weather else "N/A"
    wind = weather.get("wind_speed_ms", "N/A") if weather else "N/A"
    cloud = weather.get("cloud_cover_pct", "N/A") if weather else "N/A"

    pollution = predictions.get("pollution", 0) if predictions else 0
    storm = predictions.get("storm", 0) if predictions else 0

    # =========================
    # COLOR LOGIC
    # =========================
    color = "green"
    if pollution == 2:
        color = "red"
    elif pollution == 1:
        color = "orange"

    # =========================
    # POPUP HTML (CLEAN UI)
    # =========================
    popup_html = f"""
    <div style="font-family: Arial; font-size: 13px;">
        <b>🌍 Environment Data</b><br><br>
        🌡 Temp: {temp} °C<br>
        💧 Humidity: {humidity} %<br>
        💨 Wind: {wind} m/s<br>
        ☁ Cloud: {cloud} %<br>
    </div>
    """

    # =========================
    # MAIN MARKER
    # =========================
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_html, max_width=250),
        icon=folium.Icon(color=color, icon="leaf", prefix="fa")
    ).add_to(marker_cluster)

    # =========================
    # STORM VISUALIZATION
    # =========================
    if storm == 1:
        folium.Circle(
            location=[lat, lon],
            radius=5000,
            color="red",
            fill=True,
            fill_opacity=0.2,
            tooltip="⚡ Storm Risk Area"
        ).add_to(m)

    # =========================
    # LAYER CONTROL
    # =========================
    folium.LayerControl(collapsed=False).add_to(m)

    # =========================
    # ENSURE OUTPUT DIR
    # =========================
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    file_path = os.path.join(OUTPUT_DIR, MAP_FILE)

    # =========================
    # SAVE MAP
    # =========================
    m.save(file_path)

    return file_path