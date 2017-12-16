import lxml.html
import codecs
import requests
import database
import urllib.request
import site_downloader


class Scraping:

    def __init__(self):
        self.url = 'https://www.globaltennisnetwork.com/tennis-courts/courts/country/223-united-states'
        self.default_url = 'https://www.globaltennisnetwork.com'
        self.states_links = []
        self.courts_data = []
        self.cities_links = []
        self.courts_links = []

    def get_states_links(self):
        downloader = site_downloader.Downloader(self.url, 'C:/Users/Kuba/PycharmProjects/globaltennisnetwork')
        downloader.download()
        self.country_source = codecs.open('site.html', 'r', 'utf-8').read()
        self.tree = lxml.html.fromstring(self.country_source)
        self.etree = self.tree.xpath('//table[@class="table table-striped"]//tr')
        for element in self.etree:
            self.link = element.xpath('./td/a[@href]')
            self.name = element.xpath('./td/text()')
            if self.link:
                self.states_links.append([self.name, self.link[0].get('href')])
                return True

    def get_cities_links(self):
        for state, state_link in self.states_links:
            self.state_source = requests.get(self.default_url+state_link)
            self.tree = lxml.html.fromstring(self.state_source.content)
            self.etree = self.tree.xpath('//table[@class="table table-striped"]//tr')
            for element in self.etree:
                self.link = element.xpath('./td[1]/a[@href]')
                try:
                    self.cities_links.append(self.link[0].get('href'))
                except IndexError:
                    pass

    def get_courts_links(self):
        for city_link in self.cities_links:
            self.city_source = requests.get(self.default_url+city_link)
            self.city_tree = lxml.html.fromstring(self.city_source.content)
            self.city_etree = self.city_tree.xpath('//table[@class="table table-striped"]//tr/td[1]')
            for element in self.city_etree:
                self.court_link = element.xpath('./a[@href]')
                try:
                    self.courts_links.append(self.court_link[0].get('href'))
                    print(self.court_link[0])
                except IndexError:
                    pass

    def get_courts_data(self):
        for court_link in self.courts_links:
            self.court_source = requests.get(self.default_url+court_link)
            self.data_tree = lxml.html.fromstring(self.court_source.content)
            self.data_etree = self.data_tree.xpath('//div[@class="span5"]/div[1]')
            for element in self.data_etree:
                self.name = element.xpath('./h1/text()')
                self.address = element.xpath('.//div[@itemprop="address"]/span/text()')
                self.postal_code = element.xpath('.//span[@itemprop="postalCode"]/text()')
                print(self.name[0], self.address[0], self.postal_code[0])
                self.courts_data.append([self.name[0], self.address[0], self.postal_code[0]])

    def save(self):
        Database = database.Database('data', ('name', 'address', 'postal_code'))
        Database.create_database()
        for data in self.courts_data:
            Database.insert_data(data)
        Database.commit_changes()


Scraping = Scraping()
Scraping.get_states_links()
Scraping.get_cities_links()
Scraping.get_courts_links()
Scraping.get_courts_data()
Scraping.save()
