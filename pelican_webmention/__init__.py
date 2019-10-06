from pelican import signals

from pelican_webmention.bridgy import attach_bridgy_syndication_gen, \
    bridgify_content, init_bridgy_metadata
from pelican_webmention.webmention import setup_webmentions, process_discussion
from pelican_webmention.outgoing import queue_outgoing_gen


def register():
    # when article metadata has been read
    signals.article_generator_context.connect(setup_webmentions)
    signals.article_generator_context.connect(init_bridgy_metadata)
    signals.page_generator_context.connect(init_bridgy_metadata)
    signals.static_generator_context.connect(init_bridgy_metadata)

    # when content is being loaded for an article/page
    signals.content_object_init.connect(bridgify_content)

    # articles have been loaded and converted to HTML
    signals.article_generator_finalized.connect(attach_bridgy_syndication_gen)
    signals.article_generator_finalized.connect(process_discussion)
    signals.article_generator_finalized.connect(queue_outgoing_gen)
