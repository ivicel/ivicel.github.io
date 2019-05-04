#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import os
import sys

from pelicanconf import *
from pelicanconf import *

# This file is only used if you use `make publish` or

sys.path.append(os.curdir)

# If your site is available via HTTPS, make sure SITEURL begins with https://
SITEURL = 'https://ivicel.info'
RELATIVE_URLS = False

FEED_ALL_ATOM = 'feeds/all.atom.xml'
CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'

DELETE_OUTPUT_DIRECTORY = True

# Following items are often useful when publishing
#GOOGLE_ANALYTICS = ""
#DISQUS_SITENAME = ""
