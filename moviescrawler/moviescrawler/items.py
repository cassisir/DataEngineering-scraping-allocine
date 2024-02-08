# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    image = scrapy.Field()
    genre = scrapy.Field()
    date = scrapy.Field()
    synopsis = scrapy.Field()
    cast = scrapy.Field()
    ratings = scrapy.Field()

class PersonItem(scrapy.Item):  # Un item pour chaque membre du casting d'un film
    name = scrapy.Field()
    role = scrapy.Field()

