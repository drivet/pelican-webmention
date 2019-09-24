import json
import os
from pelican_webmention.webmention import load_webmentions, \
    process_discussion, Discussion


WEBMENTION_01 = {
    "sourceUrl": "https://source01.com/stuff.html",
    "targetUrl": "https://target.com/stuff1.html",
    "parsedSource": {
        "items": [
            {
                "type": ["h-entry"],
                "properties": {
                    "name": ["First mention"],
                    "content": ["this is awesome content"]
                },
                "children": [
                    {
                        "type": ["h-card"],
                        "properties": {
                            "name": ["Desmond Rivet"],
                            "url": ["https://desmondrivet.com"]
                        }
                    }
                ]
            }
        ]
    }
}

WEBMENTION_02 = {
    "sourceUrl": "https://source02.com/stuff.html",
    "targetUrl": "https://target.com/stuff2.html",
    "parsedSource": {
        "items": [
            {
                "type": ["h-entry"],
                "properties": {
                    "name": ["First mention"],
                    "content": ["this is awesome content"],
                    'in-reply-to': ['https://target.com/stuff2.html']
                },
                "children": [
                    {
                        "type": ["h-card"],
                        "properties": {
                            "name": ["Desmond Rivet"],
                            "url": ["https://desmondrivet.com"]
                        }
                    }
                ]
            }
        ]
    }
}

WEBMENTION_03 = {
    "sourceUrl": "https://source03.com/stuff.html",
    "targetUrl": "https://target.com/stuff2.html",
    "parsedSource": {
        "items": [
            {
                "type": ["h-entry"],
                "properties": {
                    "name": ["First mention"],
                    "content": ["this is awesome content"]
                },
                "children": [
                    {
                        "type": ["h-card"],
                        "properties": {
                            "name": ["Desmond Rivet"],
                            "url": ["https://desmondrivet.com"]
                        }
                    }
                ]
            }
        ]
    }
}


def setup():
    os.mkdir('/tmp/webmentions')
    save_json('/tmp/webmentions/wm01.json', WEBMENTION_01)
    save_json('/tmp/webmentions/wm02.json', WEBMENTION_02)
    save_json('/tmp/webmentions/wm03.json', WEBMENTION_03)


def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)


class Article(object):
    def __init__(self, url):
        self.url = url
        self.discussion = Discussion()


class Generator(object):
    def __init__(self):
        self.articles = []
        self.settings = {'WEBMENTION_FOLDER': '/tmp/webmentions'}


def test_attach_webmentions():
    a1 = Article('stuff1.html')
    a2 = Article('stuff2.html')
    g = Generator()
    g.articles = [a1, a2]
    process_discussion(g)

    assert len(a1.discussion.unclassified) == 1
    assert len(a2.discussion.unclassified) == 1
    assert len(a2.discussion.replies) == 1


def test_load_webmentions():
    all_wm = load_webmentions('/tmp/webmentions')
    assert len(all_wm) == 2
    assert '/stuff1.html' in all_wm
    assert '/stuff2.html' in all_wm


def teardown():
    os.remove('/tmp/webmentions/wm01.json')
    os.remove('/tmp/webmentions/wm02.json')
    os.remove('/tmp/webmentions/wm03.json')
    os.rmdir('/tmp/webmentions')
