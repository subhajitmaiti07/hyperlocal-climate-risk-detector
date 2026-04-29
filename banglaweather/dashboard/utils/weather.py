import requests
import numpy as np
from django.conf import settings
from datetime import datetime

pressure_history = []
MAX_HISTORY = 5


def fetch_weather(city="Kolkata"):
    global pressure_history

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={settings.API_KEY}&units=metric"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("API error:", e)
        return None

    main = data["main"]
    wind = data.get("wind", {})
    clouds = data.get("clouds", {})

    temp = main["temp"]
    humidity = main["humidity"]
    pressure = main.get("pressure", 1013)

    wind_speed = wind.get("speed", 0)
    wind_deg = wind.get("deg", 0)
    cloud = clouds.get("all", 0)

    rain_1h = data.get("rain", {}).get("1h", 0)

    # pressure trend
    pressure_history.append(pressure)
    if len(pressure_history) > MAX_HISTORY:
        pressure_history.pop(0)

    pressure_trend = (
        pressure_history[-1] - pressure_history[0]
        if len(pressure_history) > 1 else 0
    )

    wind_dir_sin = np.sin(np.radians(wind_deg))
    wind_dir_cos = np.cos(np.radians(wind_deg))
    heat_index = temp + 0.33 * humidity - 4

    return {
        "city": city,
        "lat": data["coord"]["lat"],
        "lon": data["coord"]["lon"],
        "temperature_C": temp,
        "humidity_pct": humidity,
        "pressure_hPa": pressure,
        "pressure_trend": pressure_trend,
        "wind_speed_ms": wind_speed,
        "wind_direction_deg": wind_deg,
        "wind_dir_sin": wind_dir_sin,
        "wind_dir_cos": wind_dir_cos,
        "cloud_cover_pct": cloud,
        "precip_mm": rain_1h,
        "heat_index": heat_index,
        "dew_point_C": temp - ((100 - humidity) / 5),
        "solar_radiation_Wm2": 500,
        "et0_mm": 3,
        "city_encoded": 1,
        "hour": datetime.now().hour,
        "month": datetime.now().month
    }