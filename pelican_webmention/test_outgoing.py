from pelican_webmention.outgoing import queue_outgoing


class Article(object):
    def __init__(self, url, content):
        self.url = url
        self.content = content


input_headers = ['in_reply_to', 'repost_of', 'like_of']


def test_should_handle_no_articles():
    articles = []
    siteurl = 'http://example.com'
    cache = {
        'excluded_domains': [],
        'results': {}
    }
    queue_outgoing(cache, siteurl, input_headers, articles)
    assert len(cache['excluded_domains']) == 0
    assert len(cache['results']) == 0


def test_should_handle_article_with_no_mentions():
    articles = [Article('stuff/blah', 'hello')]
    siteurl = 'http://example.com'
    cache = {
        'excluded_domains': [],
        'results': {}
    }
    queue_outgoing(cache, siteurl, input_headers, articles)
    assert len(cache['excluded_domains']) == 0
    assert len(cache['results']) == 1
    assert len(cache['results']['stuff/blah']) == 0


def test_should_handle_article_with_excluded_mentions():
    articles = [Article('stuff/blah',
                        'hello <a href="http://twitter.com/status/123"></a>')]
    siteurl = 'http://example.com'
    cache = {
        'excluded_domains': ['twitter.com'],
        'results': {}
    }
    queue_outgoing(cache, siteurl, input_headers, articles)
    assert len(cache['excluded_domains']) == 1
    assert len(cache['results']) == 1
    assert len(cache['results']['stuff/blah']) == 0


def test_should_handle_article_with_content_mentions():
    articles = [Article('stuff/blah',
                        'hello <a href="http://hahaha.com/status/123"></a>')]
    siteurl = 'http://example.com'
    cache = {
        'excluded_domains': [],
        'results': {}
    }
    queue_outgoing(cache, siteurl, input_headers, articles)
    assert len(cache['excluded_domains']) == 0
    assert len(cache['results']) == 1
    assert len(cache['results']['stuff/blah']) == 1
    assert cache['results']['stuff/blah'] == \
        {'http://hahaha.com/status/123': None}


def test_should_handle_article_with_header_and_content_mentions():
    articles = [Article('stuff/blah',
                        'hello <a href="http://hahaha.com/status/123"></a>')]
    articles[0].in_reply_to = ['http://reply.com/qwerty/joke']
    siteurl = 'http://example.com'
    cache = {
        'excluded_domains': [],
        'results': {}
    }
    queue_outgoing(cache, siteurl, input_headers, articles)
    assert len(cache['excluded_domains']) == 0
    assert len(cache['results']) == 1
    assert len(cache['results']['stuff/blah']) == 2
    assert cache['results']['stuff/blah'] == \
        {'http://reply.com/qwerty/joke': None,
         'http://hahaha.com/status/123': None}
