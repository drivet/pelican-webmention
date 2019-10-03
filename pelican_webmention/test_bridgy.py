from pelican_webmention.bridgy import init_bridgy_metadata, \
    attach_bridgy_syndication, bridgify_content


class Generator(object):
    def __init__(self, settings={}):
        self.settings = settings


class Article(object):
    def __init__(self, url, content=''):
        self.url = url
        self.content = content


class Instance(object):
    def __init__(self, settings, metadata, content):
        self.settings = settings
        self.metadata = metadata
        self._content = content


def test_should_init_mp_syndicate_to():
    metadata = {}
    settings = {
        'WEBMENTIONS_CONTENT_HEADERS': []
    }
    init_bridgy_metadata(Generator(settings), metadata)
    assert metadata['mp_syndicate_to'] == []


def test_should_split_mp_syndicate_to():
    metadata = {
        'mp_syndicate_to': 'hello,goodbye'
    }
    settings = {
        'WEBMENTIONS_CONTENT_HEADERS': []
    }
    init_bridgy_metadata(Generator(settings), metadata)
    assert metadata['mp_syndicate_to'] == ['hello', 'goodbye']


def test_should_init_syndication():
    metadata = {}
    settings = {
        'WEBMENTIONS_CONTENT_HEADERS': []
    }
    init_bridgy_metadata(Generator(settings), metadata)
    assert metadata['syndication'] == []


def test_should_init_content_header():
    metadata = {}
    settings = {
        'WEBMENTIONS_CONTENT_HEADERS': ['in_reply_to', 'like_of']
    }
    init_bridgy_metadata(Generator(settings), metadata)
    assert metadata['in_reply_to'] == []
    assert metadata['like_of'] == []


def test_should_split_content_headers():
    metadata = {
        'in_reply_to': 'hello,goodbye',
        'like_of': 'blah,stuff'
    }
    settings = {
        'WEBMENTIONS_CONTENT_HEADERS': ['in_reply_to', 'like_of']
    }
    init_bridgy_metadata(Generator(settings), metadata)
    assert metadata['in_reply_to'] == ['hello', 'goodbye']
    assert metadata['like_of'] == ['blah', 'stuff']


def test_should_add_locations_to_articles():
    cache = {
        'site_url': 'http://example.com',
        'excluded_domains': ['http://twitter.com'],
        'results': {
            'stuff/blah': {
                'http://reply.com/qwerty/joke': {
                    'status_code': 200,
                    'location': 'http://twitter.com/status/123'
                },
            }
        }
    }
    article = Article('stuff/blah', 'hello')
    article.syndication = ['http://prexisting.com']
    articles = [article]
    attach_bridgy_syndication(cache, articles)
    assert article.syndication == ['http://prexisting.com',
                                   'http://twitter.com/status/123']


def test_should_skip_urls_that_are_not_in_results():
    cache = {
        'site_url': 'http://example.com',
        'excluded_domains': ['http://twitter.com'],
        'results': {
            'stuff/blah': {
                'http://reply.com/qwerty/joke': {
                    'status_code': 200,
                    'location': 'http://twitter.com/status/123'
                },
            }
        }
    }
    article = Article('dummy/yolo', 'hello')
    article.syndication = ['http://prexisting.com']
    articles = [article]
    attach_bridgy_syndication(cache, articles)
    assert article.syndication == ['http://prexisting.com']


def test_should_process_mp_syndicate_tokens():
    settings = {
        'WEBMENTION_BRIDGY_MP_SYNDICATE_MAP': {
            'mp_token_1': 'twitter',
            'mp_token_2': 'twitter_no_link',
            'mp_token_3': 'twitter_maybe_link'
        },
        'WEBMENTION_BRIDGY_PUBLISH': []
    }
    metadata = {
        'mp_syndicate_to': ['mp_token_1', 'mp_token_3']
    }
    instance = Instance(settings, metadata, 'hello')
    bridgify_content(instance)
    assert instance._content == 'hello\n' + \
        '<a href="https://brid.gy/publish/twitter"></a>\n' + \
        '<a href="https://brid.gy/publish/twitter?bridgy_omit_link=maybe"></a>'


def test_should_process_header_tokens():
    settings = {
        'WEBMENTION_BRIDGY_MP_SYNDICATE_MAP': {},
        'WEBMENTION_BRIDGY_PUBLISH': [
            ('in_reply_to', 'twitter.com', 'twitter'),
            ('like_of', 'twitter.com', 'twitter_no_link')
        ]
    }
    metadata = {
        'in_reply_to': ['http://twitter.com/status/123']
    }
    instance = Instance(settings, metadata, 'hello')
    bridgify_content(instance)
    assert instance._content == 'hello\n' + \
        '<a href="https://brid.gy/publish/twitter"></a>'
