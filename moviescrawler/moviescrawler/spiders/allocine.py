import scrapy
from scrapy import Request
from urllib.parse import urljoin
from moviescrawler.items import MovieItem, PersonItem

class AllocineSpider(scrapy.Spider):
    name = "allocine"
    allowed_domains = ["allocine.fr"]
    start_urls = ["https://www.allocine.fr/films/"]


    def parse(self, response):
        # Nombre de pages a scraper
        pages_number = int(response.css('.button-md::text').extract()[-1])
        for page in range(1, 200):  # Plus de 117 000 films sur les 7830 pages, on se limite donc à 200 pages (3000 films) par contrainte de temps
            page_url = response.url+"?page="+str(page)
            yield Request(page_url, callback=self.parse_page)


    def parse_page(self, response):
        movies_urls = response.css(".meta-title-link::attr(href)").extract()
        for url in movies_urls:
            full_url = urljoin(response.url, url)
            yield Request(full_url, callback=self.parse_movie)

    def parse_movie(self, response):
        movie = MovieItem()
        movie['_id'] = response.url.split('=')[-1].split('.')[0]
        movie['title'] = response.css(".titlebar-title::text").extract_first()
        movie['image'] = response.css('div.card.entity-card img.thumbnail-img::attr(src)').extract_first()
        movie['synopsis'] = response.css('#synopsis-details .content-txt .bo-p::text').extract()
        movie['genre'] = response.css('[clas="dark-grey-link"]::text').extract()
        movie['date'] = response.css(".date::text").extract_first()

        ratings = response.css('.rating-item')
        # Vérifie que le film contient des notes
        if len(ratings)>1:
            press_rating = ratings[0].css('.stareval-note::text').get()
            spectators_rating = ratings[1].css('.stareval-note::text').get()
            movie['ratings'] = {'press': press_rating, 'spectators': spectators_rating}

        casting_url = self.get_casting_url(response.url)
        yield Request(casting_url, callback=self.parse_casting, meta={'movie_info': dict(movie)})


    def parse_casting(self, response):
        movie= MovieItem(response.meta['movie_info'])

        cast = []
        sections = response.css('.gd-col-left .section')
        for section in sections:
            title_section = section.css('.titlebar ::text').get()
            cards = section.css('.card')
            rows = section.css('.md-table-row')

            for card in cards:
                person = PersonItem()
                person['name'] = card.css('.meta-title-link ::text').get()
                person['role'] = card.css('.meta-sub::text').get()
                if not person['role']:
                    person['role']=title_section
                cast.append(person)
                

            for row in rows:
                person = PersonItem()
                if title_section == "Acteurs et actrices":
                    person['name'] = row.css('a::text').get()
                    person['role'] = row.css('span::text').get()
                elif title_section == "Scénaristes":
                    person['name'] = row.css('.link-empty::text').get()
                    person['role'] = row.css('.link-light::text').get()
                else :
                    person['name'] = row.css('.link::text').get()
                    person['role'] = row.css('.light::text').get()
                
                if not person['role']:
                    person['role']=title_section
                cast.append(person)


        movie['cast'] = cast
        yield movie


    def get_casting_url(self, movie_url):
        movie_id = movie_url.split('=')[-1].split('.')[0]
        casting_url = movie_url.split('_')[0]+'-'+movie_id+'/casting'
        return casting_url
