FROM python:3.11.5-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app/