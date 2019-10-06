import yaml


def get_content_headers(settings):
    return settings.get('WEBMENTIONS_CONTENT_HEADERS',
                        ['like_of', 'repost_of', 'in_reply_to'])


def make_anchor(url):
    return '<a href="' + url + '"></a>'


def load_cache():
    filename = 'webmention_cache.yml'
    cache = load_yaml(filename)
    if not cache:
        return {
            'excluded_domains': [],
            'results': {}
        }
    else:
        return cache


def save_cache(cache):
    filename = 'webmention_cache.yml'
    save_yaml(filename, cache)


def load_yaml(filename):
    try:
        with open(filename) as f:
            return yaml.safe_load(f)
    except Exception as exc:
        print(f'Trouble opening YAML file {filename}, error = {exc}')
        return None


def save_yaml(filename, cache):
    try:
        with open(filename, 'w') as f:
            yaml.dump(cache, f)
    except Exception as exc:
        print(f'Trouble writing YAML file {filename}, error = {exc}')
        return None
