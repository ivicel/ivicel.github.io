#!/bin/sh

git add .
git commit -m "$(date)"
pelican -s pelicanconf.py -o ivicel.github.io -d -D
git --work-tree ivicel.github.io --git-dir .git/modules/ivicel.github.io add .
git --work-tree ivicel.github.io --git-dir .git/modules/ivicel.github.io commit -m 'generate blog'
git --work-tree ivicel.github.io --git-dir .git/modules/ivicel.github.io push
