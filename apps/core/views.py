import requests
from django.http import JsonResponse
from django.conf import settings

def weather_api(request):
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")

    if not lat or not lon:
        return JsonResponse({"error": "Missing coordinates"}, status=400)

    key = settings.OPENWEATHER_KEY

    # ===== CLIMA OPENWEATHER =====
    weather_url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&appid={key}&units=metric&lang=es"
    )
    weather_res = requests.get(weather_url).json()

    # ===== COMUNA REAL (REVERSE GEOCODING) =====
    nominatim_url = (
        f"https://nominatim.openstreetmap.org/reverse?"
        f"format=json&lat={lat}&lon={lon}&zoom=10&addressdetails=1"
    )

    geo_res = requests.get(
        nominatim_url,
        headers={"User-Agent": "gymofthrones/1.0"}  # <-- FIX ✔
    ).json()

    comuna = (
        geo_res.get("address", {}).get("suburb")
        or geo_res.get("address", {}).get("city")
        or geo_res.get("address", {}).get("town")
        or geo_res.get("address", {}).get("municipality")
        or "Comuna desconocida"
    )

    return JsonResponse({
        "temp": round(weather_res["main"]["temp"]),
        "condition": weather_res["weather"][0]["main"],
        "location": comuna,
    })
