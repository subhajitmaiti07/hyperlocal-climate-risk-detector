from django.shortcuts import render
from django.http import FileResponse
import os

from .utils.weather import fetch_weather
from .utils.ml_model import predict_all
from .utils.map_generator import generate_map


def dashboard(request):

    # 🔥 GET CITY FROM USER
    city = request.GET.get("city", "Kolkata")

    weather = fetch_weather(city)

    if not weather:
        return render(request, "dashboard/dashboard.html", {
            "error": "City not found"
        })

    predictions = predict_all(weather, None)

    # 🔥 Generate dynamic map
    generate_map(
        weather["lat"],
        weather["lon"],
        weather,
        predictions
    )

    return render(request, "dashboard/dashboard.html", {
        "weather": weather,
        "predictions": predictions,
        "storm_prob": predictions.get("storm_prob", 0),
        "city": city
    })


def serve_map(request):
    path = "outputs/maps/realtime_map.html"

    if os.path.exists(path):
        return FileResponse(open(path, 'rb'), content_type='text/html')
    else:
        return FileResponse(b"Map not generated yet", content_type='text/plain')