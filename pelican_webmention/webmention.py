import os
import json
import mf2util
from urllib.parse import urlparse


class Discussion(object):
    def __init__(self):
        self.likes = []
        self.reposts = []
        self.replies = []
        self.self_replies = []
        self.unclassified = []


def setup_webmentions(generator, metadata):
    metadata['discussion'] = Discussion()


def process_discussion(generator):
    all_webmentions = load_webmentions(generator.settings['WEBMENTION_FOLDER'])
    all_articles = {}
    for article in list(generator.articles):
        # save indexed article for lookup later
        all_articles[f'/{article.url}'] = article
        attach_webmentions(article, all_webmentions)

    for article in list(generator.articles):
        attach_article_to_parent(article, all_articles)


def load_webmentions(wm_root):
    all_webmentions = {}
    for root, dirs, files in os.walk(wm_root):
        for f in files:
            wm_path = os.path.join(wm_root, root, f)
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
    wm = all_webmentions[f'/{article.url}']
    comment = mf2util.interpret_comment(wm['parsedSource'],
                                        wm['sourceUrl'],
                                        [wm['targetUrl']])
    if comment['comment_type']:
        comment_type = comment['comment_type'][0]
        if comment_type == 'like':
            article.discussion.likes.append(comment)
        elif comment_type == 'repost':
            article.discussion.reposts.append(comment)
        elif comment_type == 'reply':
            article.discussion.replies.append(comment)
        else:
            print(f'Unrecognized comment type: {comment_type}')
            article.discussion.unclassified.append(comment)
    else:
        print('No comment type parsed')
        article.discussion.unclassified.append(comment)


def attach_article_to_parent(article, all_articles):
    if not article.in_reply_to:
        return

    in_reply_to = startslash(urlparse(article.in_reply_to).path)

    if in_reply_to not in all_articles:
        return

    all_articles[in_reply_to].discussion.self_replies.append(article)


def read_whole_file(filename):
    with open(filename, 'r') as content_file:
        content = content_file.read()
    return content


def startslash(url):
    if url.startswith('/'):
        return url
    else:
        return f'/{url}'
