from django.urls import path
from .views import weather_api


urlpatterns = [
    path("api/weather/", weather_api, name="weather_api"),

]
