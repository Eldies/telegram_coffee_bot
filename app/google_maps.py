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


def get_timezone_for_location(latitude: int, longitude: int) -> str:
    # https://developers.google.com/maps/documentation/timezone/requests-timezone?hl=en_US
    response = requests.get(
        url='https://maps.googleapis.com/maps/api/timezone/json',
        params=dict(
            key=settings.GOOGLE_MAPS_API_KEY,
            location='{},{}'.format(latitude, longitude),
            timestamp=0,
        ),
    )
    result = response.json()
    if result['status'] not in ('OK',):
        raise GoogleApiError(result.get('error_message', 'no error message'))

    return result['timeZoneId']
