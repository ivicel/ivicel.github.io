#!/bin/sh

git add .
git commit -m "generate blog at $(date)"
git push origin source
