from django import forms


class CitySearchForm(forms.Form):
    """Форма для поиска города."""

    city = forms.CharField(max_length=100, label='Название города:')
