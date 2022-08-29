# -*- coding: utf-8 -*-
import requests

from . import settings
from .exceptions import GoogleApiError


def get_city_data(city: str) -> dict:
    response = requests.get(
        url='https://maps.googleapis.com/maps/api/geocode/json',
        params=dict(
            key=settings.GOOGLE_MAPS_API_KEY,
            address=city,
            language='ru',
        ),
    )
    result = response.json()
    if result['status'] not in ('OK', 'ZERO_RESULTS'):
        raise GoogleApiError(result.get('error_message', 'no error message'))

    return result
