#!/usr/bin/env python3
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'ivicel'
SITENAME = 'Amber time'
SITEURL = 'https://io.ivicel.info'

PATH = 'content'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = 'zh'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
CACHE_CONTENT = False

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10


# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
THEME = 'pelican-bootstrap3'

PLUGIN_PATHS = ['plugins']
PLUGINS = ['i18n_subsites']
PYGMENTS_STYLE = 'default'
JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}
MARKDOWN = {
    "extensions": [
    "codehilite(css_class=highlight)", "extra", "toc", 'def_list',
    'sane_lists',
    'headerid',
    'attr_list',
    'tables',
    'toc',
    ]
}
