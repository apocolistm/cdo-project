import requests
from lxml import html
from models import RawProduct, Product, Shop
from db import init_db
from config import Mongo
import zlib

init_db(Mongo)
SHOP = 'likemobmarket'


def parse_sitemap():
    url = 'https://likemobmarket.ru/sitemap.xml'

    r = requests.get(url)
    r.raise_for_status()

    links = []
    tree = html.fromstring(r.content)
    for child in tree.iterchildren():
        link = child.find('loc').text.strip()
        links.append(link)

    return links


def parse_products():
    init_db(Mongo)
    parsed_links = [r.link for r in RawProduct.objects(shop=SHOP)]
    links = parse_sitemap()
    links = [i for i in links if i not in parsed_links]

    for i, link in enumerate(links):
        print(f'{i + 1}/{len(links)}')
        r = requests.get(link, timeout=10)
        tree = html.fromstring(r.content)
        availability = tree.xpath('string(//meta[@property="product:availability"]/@content)')
        if not availability:
            print(link)
            continue

        product = RawProduct(
            shop=SHOP,
            link=link,
            title=tree.xpath('string(//meta[@property="og:title"]/@content)'),
            article=tree.xpath('string(//meta[@property="product:retailer_item_id"]/@content)'),
            tags=tree.xpath('string(//meta[@name="keywords"]/@content)').split(','),
            description=tree.xpath('string(//meta[@name="description"]/@content)').strip(),
            price=tree.xpath('string(//div[@class="PActualPrice"]/span[@class="Price"]/text())'),
            image=tree.xpath('string(//meta[@property="og:image"]/@content)'),
            availability=False if availability == 'out of stock' else True,
            html=zlib.compress(r.content),
        )
        product.save()


def prepare_products():
    products = []
    for product in RawProduct.objects(shop=SHOP):
        products.append(Product(
            shop=SHOP,
            url=product.link,
            title=product.title,
            article=product.article,
            tags=product.tags,
            description=product.description,
            price=int(product.price.replace(' ', '').strip()) if product.price else None,
            image=product.image,
            availability=product.availability,
            currency='RUB',
        ))

    Product.objects.insert(products)


def add_shop():
    shop = Shop.objects(slug=SHOP).first() or Shop(slug=SHOP)
    shop.update(
        name='LikeMob',
        company='ИП Оганнисян Амаяк Артурович',
        site='https://likemobmarket.ru',
        upsert=True,
    )


prepare_products()
