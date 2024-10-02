FROM python:3.12

RUN mkdir /to_do

WORKDIR /to_do

COPY ./requirements.txt .

RUN pip install psycopg2-binary

RUN pip install -r requirements.txt

COPY . .