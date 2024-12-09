import scrapy
from pymongo import MongoClient
from urllib.parse import urljoin
import datetime

client = MongoClient("mongodb+srv://test:test123@cluster0.s7jei.mongodb.net/")
db = client.scrappy

def insertoDb(page, title, rating, image, price):
    collections = db[page]
    doc = {
        "title": title,
        "rating": rating,
        "image": image,
        "price": price,
        "scraped_at": datetime.datetime.utcnow()
    }
    inserted = collections.insert_one(doc)
    return inserted.inserted_id

class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = [
        "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
        "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
    ]

    def parse(self, response):
        page = response.url.split("/")[-2]
        cards = response.css(".product_pod")
        for card in cards:
            title = card.css("h3>a::text").get()
            rating = card.css(".star-rating").attrib["class"].split(" ")[1]
            image_url = urljoin(response.url, card.css(".image_container img::attr(src)").get())
            price = card.css(".product_price p::text").get().strip()

            try:
                insertoDb(page, title, rating, image_url, price)
                self.log(f"Inserted: {title} into collection {page}")
            except Exception as e:
                self.log(f"Failed to insert {title}: {e}")
