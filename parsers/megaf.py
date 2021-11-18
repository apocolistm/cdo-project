import requests
from lxml import html
from models import RawProduct, Product, Shop
from db import init_db
from config import Mongo
import zlib

init_db(Mongo)
SHOP = 'megaf'


def parse_sitemap():
    url = 'https://www.mega-f.ru/sitemap.xml'

    r = requests.get(url)
    r.raise_for_status()

    links = []
    tree = html.fromstring(r.content)
    for child in tree.iterchildren():
        link = child.find('loc').text.strip()
        if link.endswith('detail'):
            links.append(link)

    return links


def parse_products():
    parsed_links = [r.link for r in RawProduct.objects(shop=SHOP)]
    links = parse_sitemap()
    links = [i for i in links if i not in parsed_links]

    for i, link in enumerate(links):
        print(f'{i + 1}/{len(links)}')
        r = requests.get(link, timeout=10)
        tree = html.fromstring(r.content)
        product = RawProduct(
            shop=SHOP,
            link=link,
            title=tree.xpath('string(//meta[@name="title"]/@content)'),
            article=tree.xpath('string(//div[@class="product-article"]/text())').split(': ')[1].strip(),
            tags=tree.xpath('string(//meta[@name="description"]/@content)').split('; '),
            description=tree.xpath('string(//div[@class="product-description"]/text())').strip(),
            price=tree.xpath('string(//main//div[@class="product-price"]//span[@class="PricesalesPrice"]/text())'),
            image=tree.xpath('string(//img[@class="product-image"]/@src)'),
            availability=True,
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
            price=int(product.price.replace('руб.', '').replace(' ', '').strip()) if product.price else None,
            image='https://www.mega-f.ru' + product.image,
            availability=product.availability,
            currency='RUB',
        ))

    Product.objects.insert(products)


def add_shop():
    shop = Shop.objects(slug=SHOP).first() or Shop(slug=SHOP)
    shop.update(
        name='MEGA-F',
        company='ООО "Мега-Ф Холдинг"',
        site='https://www.mega-f.ru',
        upsert=True,
    )


add_shop()
