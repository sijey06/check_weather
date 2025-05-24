from django.test import TestCase, Client
from django.urls import reverse
from weather.forms import CitySearchForm
import json
import responses


class WeatherAppTests(TestCase):
    """Класс тестов для приложения прогноза погоды."""

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()

    def test_form_view_get_request(self):
        """Проверка доступа к главной странице формы поиска города."""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'weather/index.html')
        self.assertIsInstance(response.context['form'], CitySearchForm)

    def test_form_view_post_valid_city(self):
        """Проверка валидной отправки формы с названием города."""
        data = {'city': 'Москва'}
        response = self.client.post(reverse('index'), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/weather/', response.url)

    def test_get_weather_view_with_valid_city(self):
        """Проверка корректности отображения прогноза погоды."""
        with responses.RequestsMock() as rsps:
            geo_json = [
                {"lat": "55.75", "lon": "37.62"}
            ]
            rsps.add(
                rsps.GET,
                'https://geocode.maps.co/search?q=Москва',
                body=json.dumps(geo_json),
                status=200,
                content_type='application/json'
            )
            openmeteo_json = {
                "current_weather": {
                    "temperature": 20,
                    "windspeed": 5
                },
            }
            rsps.add(
                rsps.GET,
                'https://api.open-meteo.com/v1/forecast?',
                body=json.dumps(openmeteo_json),
                status=200,
                content_type='application/json'
            )

            response = self.client.get(reverse('get_weather') + '?city=Москва')
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'weather/result.html')
            self.assertContains(response, 'Москва')
            self.assertContains(response, '20°C')
            self.assertContains(response, '5 м/с')

    def test_get_weather_view_with_invalid_city(self):
        """Проверка на сообщение об ошибке, для не действительного города."""
        with responses.RequestsMock() as rsps:
            rsps.add(
                rsps.GET,
                'https://geocode.maps.co/search?q=InvalidCity',
                body=json.dumps([]),
                status=200,
                content_type='application/json'
            )

            response = self.client.get(
                reverse('get_weather') + '?city=InvalidCity'
            )
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'weather/result.html')
            self.assertContains(response, 'Город не найден')
