from pelican_webmention.utils import load_cache, make_anchor
from urllib.parse import urlparse


PUBLISH_TWITTER = 'https://brid.gy/publish/twitter'

PUBLISH_TOKENS = {
    'twitter': PUBLISH_TWITTER,
    'twitter_no_link': f'{PUBLISH_TWITTER}?bridgy_omit_link=true',
    'twitter_maybe_link': f'{PUBLISH_TWITTER}?bridgy_omit_link=maybe'
}


def init_bridgy_metadata(generator, metadata):
    if 'mp_syndicate_to' not in metadata:
        metadata['mp_syndicate_to'] = []
    elif isinstance(metadata['mp_syndicate_to'], str):
        # so we can handle traditional markdown metadata
        metadata['mp_syndicate_to'] = metadata['mp_syndicate_to'].split(',')

    # these headers normally come from micropub, and will heance be lists,
    # but when they come from a traditional Markdown file (where they are
    # strings) we need to turn the values into lists
    for header in generator.settings['WEBMENTIONS_CONTENT_HEADERS']:
        if header not in metadata:
            metadata[header] = []
        elif isinstance(metadata[header], str):
            metadata[header] = metadata[header].split(',')

    # Initialize if syndication is not there.  Other plugins could mess with
    # this attribute so be careful
    if 'syndication' not in metadata:
        metadata['syndication'] = []


# alter the content of the article so that we will send webmention to bridgy
# if required
def bridgify_content(instance):
    publish_tokens = []
    settings = instance.settings

    mp_syndicate_map = settings['WEBMENTION_BRIDGY_MP_SYNDICATE_MAP']
    for token in instance.metadata.get('mp_syndicate_to', []):
        if token in mp_syndicate_map and \
           mp_syndicate_map[token] not in publish_tokens:
            publish_tokens.append(mp_syndicate_map[token])

    publish_headers = settings['WEBMENTION_BRIDGY_PUBLISH']

    for ph in publish_headers:
        (header, domain, token) = ph
        if header not in instance.metadata:
            continue

        for header_url in instance.metadata[header]:
            url = urlparse(header_url)
            if url.hostname == domain and token not in publish_tokens:
                publish_tokens.append(token)

    bridgy_urls = [PUBLISH_TOKENS[token] for token in publish_tokens]
    bridgy_anchors = [make_anchor(url) for url in bridgy_urls]
    if len(bridgy_anchors) > 0:
        instance._content += '\n' + '\n'.join(bridgy_anchors)


def attach_bridgy_syndication_pelican(generator):
    """Entry point for pelican"""
    attach_bridgy_syndication(load_cache(), generator.articles)


def attach_bridgy_syndication(cache, articles):
    """Attach a bridgy specific syndication value to the article metadata using
    the webmention cache file, in case template want to make use of the
    result.

    Basically, any webmention result with a saved 'location' header is
    treated as a bridgy webmention abd the location is treated as a
    syndication location.

    """
    for article in list(articles):
        url = article.url
        if url not in cache['results']:
            continue

        target_results = cache['results'][url]

        locations = [r['location'] for r in list(target_results.values())
                     if 'location' in r]

        article.syndication += locations
