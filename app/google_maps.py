# -*- coding: utf-8 -*-
import requests

from . import settings


def get_city_data(city: str) -> dict:
    result = requests.get(
        url='https://maps.googleapis.com/maps/api/geocode/json',
        params=dict(
            key=settings.GOOGLE_MAPS_API_KEY,
            address=city,
            language='ru',
        ),
    )
    return result.json()
