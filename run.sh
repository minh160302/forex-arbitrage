#! /bin/bash

node ./scraping/forex.js

jupyter nbconvert --to script main.ipynb

python main.py