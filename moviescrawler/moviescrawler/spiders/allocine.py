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
        pages_number = int(response.css('.button-md::text').extract()[-1])      # Récupère le nombre de pages
        for page in range(1, 3):                                               # Plus de 117 000 films sur les 7830 pages, on se limite donc à 200 pages (3000 films) par contrainte de temps
            page_url = response.url+"?page="+str(page)                          # Récupère l'url de la page à parcourir
            yield Request(page_url, callback=self.parse_page)                   # Accède à la page


    def parse_page(self, response):
        movies_urls = response.css(".meta-title-link::attr(href)").extract()    # Récupère les urls de tous les films de la page
        for url in movies_urls:                                                 # Parcourt tous les films de la page
            full_url = urljoin(response.url, url)
            yield Request(full_url, callback=self.parse_movie)                  # Accède à l'url du film

    def parse_movie(self, response):
        movie = MovieItem()
        movie['_id'] = response.url.split('=')[-1].split('.')[0]                                                # Extraction de l'id du film
        movie['title'] = response.css(".titlebar-title::text").extract_first()                                  # Extraction du titre
        movie['image'] = response.css('div.card.entity-card img.thumbnail-img::attr(src)').extract_first()      # Extraction de l'affiche
        movie['synopsis'] = response.css('#synopsis-details .content-txt .bo-p::text').extract()                # Extraction du synopsis
        movie['genre'] = response.css('[clas="dark-grey-link"]::text').extract()                                # Extraction des genres
        movie['date'] = response.css(".date::text").extract_first()                                             # Extraction de la date de sortie

        ratings = response.css('.rating-item')
        # Vérifie que le film contient des notes
        if len(ratings)>1:                                                                                      # Si le film est noté
            press_rating = ratings[0].css('.stareval-note::text').get()                                         # Extraction de la note press
            spectators_rating = ratings[1].css('.stareval-note::text').get()                                    # Extraction de la note spectateurs
            movie['ratings'] = {'press': press_rating, 'spectators': spectators_rating}

        casting_url = self.get_casting_url(response.url)                                                        # Récupère l'url du casting du film
        yield Request(casting_url, callback=self.parse_casting, meta={'movie_info': dict(movie)})               # Poursuit le scraping à l'url du casting (transmet les infos déjà scrapées avec le paramètre meta)


    def parse_casting(self, response):
        movie= MovieItem(response.meta['movie_info'])                               # Récupère les infos relatives au film transmise par le paramètre meta

        cast = []
        sections = response.css('.gd-col-left .section')                            # Récupère toutes les sections du casting (réalisateurs, acteurs, doubleurs...)
        for section in sections:                                                    # Pour chaque section
            title_section = section.css('.titlebar ::text').get()                   # Récupère le titre de la section 
            cards = section.css('.card')                                            # Récupère tous les membres de la section contenus dans des cartes
            rows = section.css('.md-table-row')                                     # Et tous les autres (qui sont dans une ligne)

            for card in cards:                                                      # Pour chaque carte
                person = PersonItem()                                               # On crée un item PersonItem
                person['name'] = card.css('.meta-title-link ::text').get()          # On récupère le nom du membre du casting
                person['role'] = card.css('.meta-sub::text').get()                  # On récupère son rôle
                if not person['role']:                                              # Si le rôle de la personne n'est pas indiqué
                    person['role']=title_section                                    # on utilise le titre de la section
                cast.append(person)                                                 # Ajoute l'item à la liste du casting du film
                

            for row in rows:                                                        # Pour chaque membre du casting qui n'est pas dans une carte
                person = PersonItem()
                if title_section == "Acteurs et actrices":                          # On distingue 3 types de sections : "Acteurs et actrices", "Scénaristes" et le reste
                    person['name'] = row.css('a::text').get()                       # Chacune à une particularité pour récupérer les informations "name" et "role"
                    person['role'] = row.css('span::text').get()
                elif title_section == "Scénaristes":
                    person['name'] = row.css('.link-empty::text').get()
                    person['role'] = row.css('.link-light::text').get()
                else :
                    person['name'] = row.css('.link::text').get()
                    person['role'] = row.css('.light::text').get()
                
                if not person['role']:
                    person['role']=title_section
                cast.append(person)                                                 # Ajoute l'item à la liste du casting du film


        movie['cast'] = cast                                                        # Ajoute la liste du casting dans le champs 'cast' de l'item du film (MovieItem)
        yield movie


    def get_casting_url(self, movie_url):
        """
        Retourne l'url de la page du casting d'un film à partir de l'url du film
        """
        movie_id = movie_url.split('=')[-1].split('.')[0]                   # Récupère l'id du film
        casting_url = movie_url.split('_')[0]+'-'+movie_id+'/casting'       # Modifie l'url du film pour obtenir l'url du casting
        return casting_url                                                  # Retourne l'url du casting
