# -*- coding: utf-8 -*-
import pytest

from app.exceptions import GoogleApiError
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
        assert result['results'][0]['types'] == ['locality', 'political']
        assert result['results'][0]['geometry']['location'] == {'lat': 38.9071923, 'lng': -77.0368707}

    @pytest.mark.parametrize('get', [
        make_city_data_response(status='INVALID_REQUEST'),
        make_city_data_response(status='OVER_DAILY_LIMIT'),
        make_city_data_response(status='OVER_QUERY_LIMIT'),
        make_city_data_response(status='REQUEST_DENIED'),
        make_city_data_response(status='UNKNOWN_ERROR'),
    ], indirect=['get'])
    def test_not_ok_status(self, get):
        with pytest.raises(GoogleApiError):
            get_city_data('text')
        assert get.call_count == 1
        assert get.call_args.kwargs == dict(
            params=dict(
                address='text',
                key='api_key',
                language='ru',
            ),
            url='https://maps.googleapis.com/maps/api/geocode/json',
        )


class TestTimezoneForLocation:
    @pytest.fixture(autouse=True)
    def _setup(self, settings):
        pass

    @pytest.mark.parametrize('get, tzid', [
        [make_timezone_for_location_response(), 'America/New_York'],
        [make_timezone_for_location_response(tz_id='Europe/Moscow'), 'Europe/Moscow'],
    ], indirect=['get'])
    def test_ok(self, get, tzid):
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
        assert result == tzid

    @pytest.mark.parametrize('get', [
        make_timezone_for_location_response(status='INVALID_REQUEST'),
        make_timezone_for_location_response(status='OVER_DAILY_LIMIT'),
        make_timezone_for_location_response(status='OVER_QUERY_LIMIT'),
        make_timezone_for_location_response(status='REQUEST_DENIED'),
        make_timezone_for_location_response(status='UNKNOWN_ERROR'),
        make_timezone_for_location_response(status='ZERO_RESULTS'),
    ], indirect=['get'])
    def test_not_ok_status(self, get):
        with pytest.raises(GoogleApiError) as excinfo:
            get_timezone_for_location(latitude=123, longitude=456)
        assert str(excinfo.value) == 'no error message'
        assert get.call_count == 1
        assert get.call_args.kwargs == dict(
            params=dict(
                key='api_key',
                timestamp=0,
                location='123,456'
            ),
            url='https://maps.googleapis.com/maps/api/timezone/json',
        )

    @pytest.mark.parametrize('get', [
        make_timezone_for_location_response(status='INVALID_REQUEST', errorMessage='custom error message'),
    ], indirect=['get'])
    def test_not_ok_status_with_error_message(self, get):
        with pytest.raises(GoogleApiError) as excinfo:
            get_timezone_for_location(latitude=123, longitude=456)
        assert str(excinfo.value) == 'custom error message'
