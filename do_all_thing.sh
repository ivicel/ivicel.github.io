#!/bin/sh

pelican -s pelicanconf.py -o out -t themes/attila -D
git --work-tree out --git-dir ivicel.github.io.git add .
git --work-tree out --git-dir ivicel.github.io.git commit -m "generate blog $(date)"
git --work-tree out --git-dir ivicel.github.io.git push origin master
git add .
git commit -m "generate blog at $(date)"
git push origin master
