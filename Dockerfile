FROM python:3.12

RUN mkdir /FastApiProject

WORKDIR /FastApiProject

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean

COPY . .

RUN chmod a+x /FastApiProject/for_docker/*.sh

