from models import Product, Shop
from db import init_db
from config import Mongo
from datetime import datetime


def generate_yml(shop_name):
    init_db(Mongo)
    shop = Shop.objects(slug=shop_name).first()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    yml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE yml_catalog SYSTEM "shops.dtd">\n'
        f'<yml_catalog date="{now}">\n<shop>\n<name>{shop.name}</name>\n<company>{shop.company}</company>\n'
        f'<url>{shop.site}</url>\n<currencies>\n<currency id="RUR" rate="1"/>\n'
        '<currency id="EUR" rate="CBRF"/>\n<currency id="USD" rate="CBRF"/>\n</currencies>\n<offers>\n'
    )

    for product in Product.objects(shop=shop.slug, price__exists=True, availability=True):
        yml += (
            f'<offer id="{product.id}" type="vendor.model" available="true">\n'
            f'<url>{product.url}</url>\n'
            f'<price>{round(product.price, 2)}</price>\n'
            f'<currencyId>{product.currency}</currencyId>\n'
        )
        if product.image:
            yml += f'<picture>{product.image}</picture>\n'
        yml += (
            f'<delivery>true</delivery>\n'
            f'<typePrefix>{product.article}</typePrefix>\n'
            f'<model>{product.title}</model>\n'
        )
        yml += f'<description>\n<![CDATA[<h3>{product.title}</h3><br><p>{product.description}</p>]]>\n</description>\n'
        yml += '<manufacturer_warranty>true</manufacturer_warranty>\n'
        yml += u'</offer>\n'

    yml += '</offers>\n</shop>\n</yml_catalog>'

    with open(f'out/{shop_name}.yml', 'w') as f:
        f.write(yml)


generate_yml('megaf')
generate_yml('likemobmarket')
