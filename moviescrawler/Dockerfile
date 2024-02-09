FROM python:3.8

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

WORKDIR /app/moviescrawler

CMD ["scrapy", "crawl", "allocine"]