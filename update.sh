#!/bin/sh

#python3 collect.py
#python3 gauges.py 41

python3 fork.py

git add .
git commit -m "update"
git push
