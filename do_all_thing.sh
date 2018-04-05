#!/bin/sh

pelican -s pelicanconf.py -o io.ivicel.info -d -D
git --work-tree io.ivicel.info --git-dir ivicel.github.io.git add .
git --work-tree io.ivicel.info --git-dir ivicel.github.io.git commit -m "generate blog $(date)"
git --work-tree io.ivicel.info --git-dir ivicel.github.io.git push origin master
git add .
git commit -m "generate blog at $(date)"
git push origin master
