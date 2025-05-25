from django.urls import path

from .views import GetWeather, WeatherForm


urlpatterns = [
    path('', WeatherForm.as_view(), name='index'),
    path('weather/', GetWeather.as_view(), name='get_weather'),
]
