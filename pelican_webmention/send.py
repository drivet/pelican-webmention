import argparse
import os
import requests
import pprint
from pelican_webmention.utils import load_cache, save_cache
from ronkyuu import sendWebmention, discoverEndpoint
from urllib.parse import urlparse


def main():
    args = get_args()
    cache = load_cache()

    if execute(args, cache):
        print(f'Saving cache (commit = {args.commit_cache})')
        save_cache(cache, args.commit_cache)


def execute(args, cache):
    to_send = get_all_webmentions(cache)
    if len(to_send) > 0:
        if not args.dry_run:
            print(f'Processing {len(to_send)} webmention attempt(s)')
            results, excluded = send_all_webmentions(cache['site_url'],
                                                     to_send)
            merge_results(cache, results, excluded)
            return True
        else:
            print('Would send these webmentions: ')
            pp = pprint.PrettyPrinter()
            pp.pprint(to_send)
            return False
    else:
        print('No webmentions to send')
        return False


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",
                        help="show what would be done but do not do it",
                        action="store_true")
    parser.add_argument("--commit-cache",
                        help="commit the cache to github if set",
                        action="store_true")
    return parser.parse_args()


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
        print(f'Processing source url: {source_url}')
        for target_url in to_send[source_url]:
            if target_url in excluded:
                continue

            if source_url not in results:
                results[source_url] = {}

            r = send_webmention(site_url, source_url, target_url)
            print(f'Result: {r}')
            if r is None:
                url = urlparse(target_url)
                excluded.add(url.hostname)
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


def send_webmention(site_url, source_url, target_url):
    abs_url = os.path.join(site_url, source_url)
    print(f'Sending webmention from {abs_url} to {target_url}')
    status, endpoint_url = discoverEndpoint(target_url)
    if status == requests.codes.ok and endpoint_url is not None:
        r = sendWebmention(abs_url, target_url, endpoint_url)
        if not r.ok:
            print(f'Webmention failed with {r.status_code}')
            print(f'Error information {r.json()}')
        return r
    else:
        print(f'Failed to discover endpoint: status: {status}, ' +
              f'endpoint: {endpoint_url}')
        return None


def merge_results(cache, results, excluded):
    for e in excluded:
        if e not in cache['excluded_domains']:
            cache['excluded_domains'].append(e)

    for source_url in results.keys():
        cache['results'][source_url] = results[source_url]


if __name__ == '__main__':
    main()
