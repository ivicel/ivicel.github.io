#!/bin/sh

pelican -s publishconf.py -t themes/clean-blog -o ivicel.info -D
git --work-tree ivicel.info --git-dir ivicel.github.io.git add .
git --work-tree ivicel.info --git-dir ivicel.github.io.git commit -m "generate blog $(date)"
git --work-tree ivicel.info --git-dir ivicel.github.io.git push origin master
git add .
git commit -m "generate blog at $(date)"
git push origin master
