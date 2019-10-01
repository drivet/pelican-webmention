import argparse
import os
import requests
import pprint
from pelican_webmention.utils import load_cache
from ronkyuu import sendWebmention
from urllib.parse import urlparse


def send_webmention(site_url, source_url, target_url):
    abs_url = os.path.join(site_url, source_url)
    print(f'sending webmention from {abs_url} to {target_url}')
    r = sendWebmention(abs_url, target_url)
    if r is None:
        print('Webmention failed due to lack of endpoint')
    elif not r.ok:
        print(f'Webmention failed with {r.status_code}')
        print(f'Error information {r.json()}')
    return r


# Return dictionary of source to target list
# These are the ones to send.
def get_all_webmentions(cache):
    results = cache['results']
    to_send = {}
    for source_url in results.keys():
        for target_url in results[source_url]:
            if results[source_url][target_url]:
                continue

            if source_url not in to_send:
                to_send[source_url] = []

            to_send[source_url].append(target_url)
    return to_send


# return dict of source_url to dict of target_url and response
# As well as excluded domains
def send_all_webmentions(site_url, to_send):
    excluded = set()
    results = {}
    for source_url in to_send.keys():
        for target_url in to_send[source_url]:
            if target_url in excluded:
                continue

            if source_url not in results:
                results[source_url] = {}

            r = send_webmention(site_url, source_url, target_url)

            if r is None:
                url = urlparse(target_url)
                excluded.append(url.hostname)
            elif r.status_code == requests.codes.created:
                results[source_url][target_url] = {
                    'status_code': r.status_code,
                    'location': r.headers['Location']
                }
            else:
                results[source_url][target_url] = {
                    'status_code': r.status_code,
                }
    return results, excluded


def merge_results(cache, results, excluded):
    for e in excluded:
        if e not in cache['excluded_domains']:
            cache['excluded_domains'].append(e)

    for source_url in results.keys():
        cache['results'][source_url] = results[source_url]


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",
                        help="show what would be done but do not do it")
    return parser.parse_args()


def main():
    args = get_args()
    cache = load_cache(os.getcwd())
    to_send = get_all_webmentions(cache)
    if not args.dry_run:
        results, excluded = send_all_webmentions(cache['site_url'], to_send)
        merge_results(cache, results, excluded)
    else:
        print('would send these webmentions: ')
        pp = pprint.PrettyPrinter()
        pp.pprint(to_send)
