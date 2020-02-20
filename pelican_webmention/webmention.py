import os
import json
import mf2util
from urllib.parse import urlparse


class Discussion(object):
    def __init__(self):
        self.likes = []
        self.reposts = []
        self.replies = []
        self.bookmarks = []
        self.unclassified = []


def setup_webmentions(generator, metadata):
    metadata['webmentions'] = Discussion()


def process_discussion(generator):
    wfolder = generator.settings.get('WEBMENTION_FOLDER', 'webmentions')
    all_webmentions = load_webmentions(wfolder)
    for article in list(generator.articles):
        attach_webmentions(article, all_webmentions)


def load_webmentions(wm_root):
    all_webmentions = {}
    for root, dirs, files in os.walk(wm_root):
        for f in files:
            wm_path = os.path.join(root, f)
            webmention = json.loads(read_whole_file(wm_path))
            target_path = extract_target_path(webmention)
            if target_path not in all_webmentions:
                all_webmentions[target_path] = []
            all_webmentions[target_path].append(webmention)
    return all_webmentions


def extract_target_path(webmention):
    targetUrl = webmention['targetUrl']
    return startslash(urlparse(targetUrl).path)


def attach_webmentions(article, all_webmentions):
    wm_for_article = all_webmentions.get(f'/{article.url}', [])
    for wm in wm_for_article:
        comment = mf2util.interpret_comment(wm['parsedSource'],
                                            wm['sourceUrl'],
                                            [wm['targetUrl']])
        if comment['comment_type']:
            comment_type = comment['comment_type'][0]
            if comment_type == 'like':
                article.webmentions.likes.append(comment)
            elif comment_type == 'repost':
                article.webmentions.reposts.append(comment)
            elif comment_type == 'reply':
                article.webmentions.replies.append(comment)
            else:
                print(f'Unrecognized comment type: {comment_type}')
                article.webmentions.unclassified.append(comment)
        else:
            if 'bookmark-of' in comment:
                article.webmentions.bookmarks.append(comment)
            else:
                print('No comment type parsed: ' + wm['sourceUrl'])
                article.webmentions.unclassified.append(comment)


def read_whole_file(filename):
    with open(filename, 'r') as content_file:
        content = content_file.read()
    return content


def startslash(url):
    if url.startswith('/'):
        return url
    else:
        return f'/{url}'
