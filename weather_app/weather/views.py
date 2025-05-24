from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
from django.urls import reverse
import requests

from .forms import CitySearchForm


class WeatherForm(FormView):
    """
    Обработка формы ввода названия города и
    перенаправление на страницу с результатами.
    """

    template_name = 'weather/index.html'
    form_class = CitySearchForm
    success_url = '/weather/'

    def form_valid(self, form):
        """Метод, вызываемый при успешном заполнении формы."""
        city = form.cleaned_data['city']
        return HttpResponseRedirect(reverse('get_weather') + '?city=' + city)


class GetWeather(TemplateView):
    """Формирование страницы с текущей погодой в выбранном городе."""

    template_name = 'weather/result.html'

    def get_context_data(self, **kwargs):
        """Метод формирования контекста для отображения прогноза погоды."""
        context = super().get_context_data(**kwargs)
        city = self.request.GET.get('city')

        # Запрос гео-данных для выбранного города
        geo_api = f'https://geocode.maps.co/search?q={city}'
        try:
            geo_response = requests.get(geo_api)
            geo_response.raise_for_status()
            results = geo_response.json()
        except requests.RequestException as err:
            context.update(
                {'error': f'Ошибка получения данных геолокации: {err}'}
            )
            return context

        if not results:
            context.update({'error': 'Город не найден'})
            return context

        # Извлечение широты и долготы для выбранного города
        try:
            lat = float(results[0]['lat'])
            lon = float(results[0]['lon'])
        except (KeyError, IndexError):
            context['error'] = 'Некорректные данные геолокации'
            return context

        # Запрос текущих погодных данных
        forecast_api = 'https://api.open-meteo.com/v1/forecast?'
        forecast_params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': True,
            'hourly': 'temperature_2m,windspeed'
        }
        try:
            weather_response = requests.get(
                forecast_api, params=forecast_params
            )
            weather_response.raise_for_status()
            weather_data = weather_response.json().get('current_weather', {})
        except requests.RequestException as err:
            context.update({'error': f'Ошибка получения данных погоды: {err}'})
            return context

        context.update({
            'city': city,
            'temperature': weather_data.get('temperature'),
            'windspeed': weather_data.get('windspeed'),
        })
        return context
