#!/bin/sh

pelican -s pelicanconf.py -o output -t themes/attila -D
git --work-tree output --git-dir ivicel.github.io.git add .
git --work-tree output --git-dir ivicel.github.io.git commit -m "generate blog $(date)"
git --work-tree output --git-dir ivicel.github.io.git push origin master
git add .
git commit -m "generate blog at $(date)"
git push origin master
