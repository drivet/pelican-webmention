from pelican_webmention.send import execute
from unittest.mock import patch


class Args(object):
    def __init__(self, dry_run):
        self.dry_run = dry_run


class Request(object):
    def __init__(self, status_code, location=None):
        self.status_code = status_code
        self.ok = self.status_code >= 200 or self.status_code <= 299
        if location:
            self.headers = {
                'Location': location
            }


@patch('pelican_webmention.send.sendWebmention')
def test_empty_queue_does_not_change_cache(send_webmention_mock):
    cache = {
        'site_url': 'http://example.com',
        'excluded_domains': [],
        'results': {
            'stuff/blah': {
                'http://reply.com/qwerty/joke': {
                    'status_code': 200,
                    'location': 'http://twitter.com/status/123'
                },
            }
        }
    }
    args = Args(False)
    execute(args, cache)
    send_webmention_mock.assert_not_called()


@patch('pelican_webmention.send.sendWebmention')
def test_should_send_successful_webmention(send_webmention_mock):
    source_url = 'http://example.com/stuff/blah'
    target_url = 'http://reply.com/qwerty/joke'
    cache = {
        'site_url': 'http://example.com',
        'excluded_domains': [],
        'results': {
            'stuff/blah': {
                target_url: None,
            }
        }
    }
    args = Args(False)
    send_webmention_mock.return_value = \
        Request(201, 'http://twitter.com/status/123')
    execute(args, cache)
    send_webmention_mock.assert_called_once_with(source_url, target_url)
    source = cache['results']['stuff/blah']
    send_result = source['http://reply.com/qwerty/joke']
    assert send_result is not None
    assert send_result['status_code'] == 201
    assert send_result['location'] == 'http://twitter.com/status/123'


@patch('pelican_webmention.send.sendWebmention')
def test_should_send_failed_webmention(send_webmention_mock):
    source_url = 'http://example.com/stuff/blah'
    target_url = 'http://reply.com/qwerty/joke'
    cache = {
        'site_url': 'http://example.com',
        'excluded_domains': [],
        'results': {
            'stuff/blah': {
                target_url: None,
            }
        }
    }
    args = Args(False)
    send_webmention_mock.return_value = Request(400)
    execute(args, cache)
    send_webmention_mock.assert_called_once_with(source_url, target_url)
    source = cache['results']['stuff/blah']
    send_result = source['http://reply.com/qwerty/joke']
    assert send_result is not None
    assert send_result['status_code'] == 400
    assert 'location' not in send_result


@patch('pelican_webmention.send.sendWebmention')
def test_should_not_send_excluded_webmention(send_webmention_mock):
    target_url = 'http://twitter.com/qwerty/joke'
    cache = {
        'site_url': 'http://example.com',
        'excluded_domains': ['http://twitter.com'],
        'results': {
            'stuff/blah': {
                target_url: None,
            }
        }
    }
    args = Args(False)
    execute(args, cache)
    send_webmention_mock.assert_not_called


@patch('pelican_webmention.send.sendWebmention')
def test_should_not_send_if_no_endpoint(send_webmention_mock):
    target_url = 'http://reply.com/qwerty/joke'
    cache = {
        'site_url': 'http://example.com',
        'excluded_domains': [],
        'results': {
            'stuff/blah': {
                target_url: None,
            }
        }
    }
    args = Args(False)
    send_webmention_mock.return_value = None
    execute(args, cache)
    send_webmention_mock.assert_not_called
    assert len(cache['excluded_domains']) == 1
    assert cache['excluded_domains'] == ['reply.com']
