#!/usr/bin/env python3
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'ivicel'
SITENAME = 'Ivicel\'s Ambertime'
SITEURL = 'https://ivicel.info'
SITETITLE = 'Ambertime'
SITESUBTITLE = 'Make memory in past times'
SITEDESCRIPTION = 'ivicel\'s thoughts and writings'
SITELOGO = '/images/favicon.ico'
FAVICON = '/images/favicon.ico'

ROBOTS = 'index, follow'

CC_LICENSE = {
    'name': 'Creative Commons Attribution-ShareAlike',
    'version': '4.0',
    'slug': 'by-sa'
}

COPYRIGHT_YEAR = 2018

STATIC_PATHS = ['images', 'extra']

EXTRA_PATH_METADATA = {
    'extra/custom.css': {
        'path': 'static/custom.css'
    },
}

CUSTOM_CSS = 'static/custom.css'
MAIN_MENU = True

DISQUS_SITENAME = ''
GOOGLE_ANALYTICS = 'UA-113622715-2'

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
# LINKS = (('Pelican', 'http://getpelican.com/'),
#         ('Python.org', 'http://python.org/'),
#         ('Jinja2', 'http://jinja.pocoo.org/'),
#         ('You can modify those links in your config file', '#'),)
#
# Social widget
# SOCIAL = (('You can add links in your config file', '#'),
#          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
THEME = 'flex'

PLUGIN_PATHS = ['/Users/ivicel/Documents/ivicel-blog/plugins']
PLUGINS = ['i18n_subsites']
PYGMENTS_STYLE = 'manni'
JINJA_ENVIRONMENT = {'extensions': ['jinja2.ext.i18n']}
MARKDOWN = {
    "extensions": [
        'codehilite',
        'extra',
        'toc',
        'def_list',
        'sane_lists',
        'headerid',
        'attr_list',
        'tables',
        'toc',
    ]
}
