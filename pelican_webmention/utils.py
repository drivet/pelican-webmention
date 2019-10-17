import yaml
import base64
import os
import requests
import json


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


def save_cache(cache, commit):
    filename = 'webmention_cache.yml'
    save_yaml(filename, cache, commit)
    if commit:
        contents = load_yaml(filename)
        url = f'{get_repo_api_root()}/{filename}'
        commit_cache(url, contents)


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


def get_repo_api_root():
    repo = os.environ['GITHUB_REPO']
    return f'https://api.github.com/repos/{repo}/contents'


def commit_cache(url, contents):
    sha = None
    fetch_response = requests.get(url, auth=(os.environ['GITHUB_USERNAME'],
                                             os.environ['GITHUB_PASSWORD']))
    if fetch_response.ok:
        sha = fetch_response.json()['sha']
    commit_file(url, contents, sha)


def commit_file(url, contents, sha):
    c = base64.b64encode(contents.encode()).decode()
    put_data = {
        'message': 'commit of ' + url,
        'content': c
    }
    if sha:
        put_data['sha'] = sha

    return requests.put(url, auth=(os.environ['GITHUB_USERNAME'],
                                   os.environ['GITHUB_PASSWORD']),
                        data=json.dumps(put_data))
