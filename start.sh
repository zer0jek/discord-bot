#!/bin/bash
apt-get update && apt-get install -y tesseract-ocr
pip install -r requirements.txt
python bot.py
