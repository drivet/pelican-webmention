import json
import os
from pelican_webmention.webmention import load_webmentions


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


def test_load_webmentions():
    all_wm = load_webmentions('/tmp/webmentions')
    assert len(all_wm) == 2
    assert '/stuff1.html' in all_wm
    assert '/stuff2.html' in all_wm


def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)


def teardown():
    os.remove('/tmp/webmentions/wm01.json')
    os.remove('/tmp/webmentions/wm02.json')
    os.rmdir('/tmp/webmentions')
