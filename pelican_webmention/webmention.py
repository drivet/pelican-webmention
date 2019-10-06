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
        self.all_replies = []
        self.unclassified = []


def setup_webmentions(generator, metadata):
    metadata['discussion'] = Discussion()


def process_discussion(generator):
    wfolder = generator.settings.get('WEBMENTION_FOLDER', '../webmentions')
    all_webmentions = load_webmentions(wfolder)
    all_articles = {}
    for article in list(generator.articles):
        # save indexed article for lookup later
        all_articles[f'/{article.url}'] = article
        attach_webmentions(article, all_webmentions)

    for article in list(generator.articles):
        attach_article_to_parent(article, all_articles)

    for article in list(generator.articles):
        d = article.discussion
        d.all_replies = d.replies + d.self_replies


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
    wm_for_article = all_webmentions.get(f'/{article.url}', [])
    for wm in wm_for_article:
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
    if not hasattr(article, 'in_reply_to') or not article.in_reply_to:
        return

    for in_reply_to_str in article.in_reply_to:
        in_reply_to = startslash(urlparse(in_reply_to_str).path)

        if in_reply_to not in all_articles:
            continue

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
