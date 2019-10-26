import os
from ronkyuu import findMentions
from pelican_webmention.utils import load_cache, save_cache, make_anchor, \
    get_content_headers


def queue_outgoing_gen(generator):
    if not generator.settings.get('WEBMENTIONS_GENERATE_OUTGOING', False):
        return

    cache = load_cache()
    queue_outgoing(cache,
                   generator.settings['SITEURL'],
                   get_content_headers(generator.settings),
                   generator.articles)
    save_cache(cache)


def queue_outgoing(cache, siteurl, content_headers, articles):
    for article in list(articles):
        url = article.url
        if url in cache['results']:
            continue

        mentions = find_mentions(article, siteurl, content_headers,
                                 cache['excluded_domains'])
        if not mentions:
            cache['results'][url] = {}
        else:
            cache['results'][url] = dict((r, None) for r in mentions['refs'])


def find_mentions(article, siteurl, content_headers, excluded):
    source_url = os.path.join(siteurl, article.url)
    mentionable_content = make_mentionable_input(article, content_headers)
    return findMentions(source_url, None, exclude_domains=excluded,
                        content=mentionable_content, test_urls=False)


def make_mentionable_input(article, input_headers):
    content = ''
    for header in input_headers:
        if not hasattr(article, header):
            continue
        value = getattr(article, header)
        if isinstance(value, str):
            content += make_anchor(value) + '\n'
        elif isinstance(value, list):
            for v in value:
                content += make_anchor(v) + '\n'
    return article.content + '\n' + content
