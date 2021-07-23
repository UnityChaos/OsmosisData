#!/bin/sh

python3 collect.py
python3 gauges.py 15
git add .
git commit -m "update"
git push
