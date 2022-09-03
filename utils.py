import logging

from telegram.utils.request import Request
from telegram.utils.types import JSONDict

from tests.utils import make_post_response


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)
old_post = Request.post


def substitute_post(self, url: str, data: JSONDict, *args, **kwargs):
    method = url.split('/')[-1]
    result = old_post(self, url, data, *args, **kwargs)
    expected_response = make_post_response(url, data)
    if method in ('setMyCommands', 'getMe', 'deleteWebhook'):
        assert result == expected_response, (method, expected_response, result)
        return result
    elif method == 'sendMessage':
        for key in expected_response:
            assert key in ('message_id', 'date') or expected_response[key] == result[key], ('sendMessage', key, expected_response[key], result[key])
        for key in result:
            assert key in ('entities') or key in expected_response, ('sendMessage', key, expected_response.keys(), result.keys())
        return result
#    elif method == 'getUpdates':
#        return old_post(self, url, *args, **kwargs)
#        return [{'update_id': 821428716, 'message': {'message_id': 33, 'from': {'id': 5000566356, 'is_bot': False, 'first_name': 'Dlavrukhin', 'last_name': 'Test', 'username': 'eldies', 'language_code': 'ru'}, 'chat': {'id': 5000566356, 'first_name': 'Dlavrukhin', 'last_name': 'Test', 'username': 'eldies', 'type': 'private'}, 'date': 1662231889, 'text': '/start', 'entities': [{'offset': 0, 'length': 6, 'type': 'bot_command'}]}}]

    logger.info('post {}'.format(url))
    logger.info(result)
    return result
