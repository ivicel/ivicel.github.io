#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'ivicel'
SITENAME = 'Ambertime'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = 'zh'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 5

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True

THEME = 'attila'

STATIC_PATHS = ['assets']

HOME_COVER = '/assets/images/header.jpg'
# COLOR_SCHEME_CSS = 'monokai.css'
CSS_OVERRIDE = ['assets/css/prism.css', 'assets/css/base.css', 'assets/css/base-control.css',
                'assets/css/github.css', 'assets/css/codemirror.css', 'assets/css/ivicel.css']
JS_OVERRIDE = ['assets/js/prism.js']

PLUGIN_PATHS = ['plugins']
PLUGINS = ['i18n_subsites', 'pelican-toc', 'sitemap', 'cjk-auto-spacing']
JINJA_ENVIRONMENT = {
    'extensions': ['jinja2.ext.i18n'],
}
JINJA_FILTERS = {'max': max}
PYGMENTS_STYLE = 'manni'
MARKDOWN = {
    "extensions": [
        # 'codehilite',
        'tables',
        'toc',
        'pymdownx.magiclink',
        # 'pymdownx.betterem',
        'pymdownx.tilde',
        'pymdownx.emoji',
        'pymdownx.tasklist',
        'pymdownx.extra'
        # 'pymdownx.superfences',
    ],
    'extension_configs': {
        'pymdownx.highlight': {
            'linenums': True,
            'use_pygments': False,
            'linenums_style': 'inline',
            'css_class': 'highlight'
        }
    },

}
