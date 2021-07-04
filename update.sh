#!/bin/sh

python3 collect.py
git add .
git commit -m "update"
git push
