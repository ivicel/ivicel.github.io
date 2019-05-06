#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

from functools import partial

PATH = 'content'
AUTHOR = 'ivicel'
SITENAME = 'Ambertime'
SITEURL = ''
SITESUBTITLE = 'Make memory in past times'
SITEDESCRIPTION = "ivicel's thoughts and writings"
SIDEBAR_ABOUT_DESCRIPTION = '只要偶尔深夜想起有你, 会有一丝微微的酒意'
SIDEBAR_AVATAR = '/assets/images/avatar.png'

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
SOCIALS = {
    'github': 'https://github.com/ivicel'
}

DEFAULT_PAGINATION = 5

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

THEME = 'clean-blog'

ARTICLE_URL = '{date:%Y}/{date:%m}/{slug}.html'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{slug}.html'
PAGE_URL = '{slug}'
PAGE_SAVE_AS = '{slug}.html'
YEAR_ARCHIVE_SAVE_AS = '{date:%Y}/index.html'
MONTH_ARCHIVE_SAVE_AS = '{date:%Y}/{date:%m}/index.html'

MENUITEMS = [
    ('archives', '/archives'),
    ('about', '/about')
]

STATIC_PATHS = ['assets']

USE_FOLDER_AS_CATEGORY = False

GOOGLE_ANALYTICS = 'UA-113622715-2'

COPYRIGHT_YEAR = 2019

HOME_COVER = 'assets/images/header.jpg'
# COLOR_SCHEME_CSS = 'monokai.css'
CSS_OVERRIDE = ['assets/css/prism.css', 'assets/css/base.css', 'assets/css/base-control.css',
                'assets/css/github.css', 'assets/css/codemirror.css', 'assets/css/ivicel.css']
JS_OVERRIDE = ['assets/js/prism.js']

PLUGIN_PATHS = ['plugins']
PLUGINS = [
    'i18n_subsites',
    # 'pelican-toc',
    'sitemap',
    # 'cjk-auto-spacing'
]

JINJA_ENVIRONMENT = {
    'extensions': [
        'jinja2.ext.i18n',
        'jinja2.ext.loopcontrols'
    ]
}
JINJA_FILTERS = {
    'sort_by_article_count': partial(sorted, key=lambda t: len(t[1]), reverse=True)
}

MARKDOWN = {
    "extensions": [
        'codehilite',
        'markdown.extensions.tables',
        'pymdownx.magiclink',
        'pymdownx.betterem',
        'pymdownx.tilde',
        'pymdownx.emoji',
        'pymdownx.tasklist',
        'pymdownx.superfences',
        'pymdownx.highlight',
        # 'pymdownx.inlinehilite'
    ],
    'extension_configs': {
        'pymdownx.highlight': {
            'linenums': True,
            'css_class': 'highlight line-numbers',
            'use_pygments': False
        }
    },

}
