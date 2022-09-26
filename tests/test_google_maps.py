# -*- coding: utf-8 -*-
import pytest

from app.google_maps import (
    get_city_data,
    get_timezone_for_location,
)
from tests.utils import (
    make_city_data_response,
    make_timezone_for_location_response,
)


class TestCityData:
    @pytest.fixture(autouse=True)
    def _setup(self, settings):
        pass

    @pytest.mark.parametrize('get', [make_city_data_response()], indirect=['get'])
    def test_ok(self, get):
        result = get_city_data('text')
        assert get.call_count == 1
        assert get.call_args.kwargs == dict(
            params=dict(
                address='text',
                key='api_key',
                language='ru',
            ),
            url='https://maps.googleapis.com/maps/api/geocode/json',
        )
        assert result['status'] == 'OK'
        assert isinstance(result['results'], list)
        assert len(result['results']) == 1
        assert result['results'][0]['formatted_address'] == 'Вашингтон, округ Колумбия, США'


class TestTimezoneForLocation:
    @pytest.fixture(autouse=True)
    def _setup(self, settings):
        pass

    @pytest.mark.parametrize('get', [make_timezone_for_location_response()], indirect=['get'])
    def test_ok(self, get):
        result = get_timezone_for_location(latitude=123, longitude=456)
        assert get.call_count == 1
        assert get.call_args.kwargs == dict(
            params=dict(
                key='api_key',
                timestamp=0,
                location='123,456'
            ),
            url='https://maps.googleapis.com/maps/api/timezone/json',
        )
        assert result == 'America/New_York'
