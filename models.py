from mongoengine import Document, StringField, ListField, BinaryField, BooleanField, IntField


class RawProduct(Document):
    meta = {'collection': 'raw_products', 'indexes': ['link', 'shop']}

    shop = StringField(required=True)
    link = StringField(required=True, unique=True)
    title = StringField(required=True)
    tags = ListField(StringField())
    article = StringField()
    description = StringField()
    price = StringField()
    image = StringField()
    availability = BooleanField(default=False)
    html = BinaryField(required=True)


class Product(Document):
    meta = {'collection': 'products', 'indexes': ['url', 'shop']}

    shop = StringField(required=True)
    url = StringField(required=True, unique=True)
    title = StringField(required=True)
    tags = ListField(StringField())
    article = StringField()
    description = StringField()
    price = IntField()
    image = StringField()
    availability = BooleanField(default=False)
    currency = StringField()


class Shop(Document):
    meta = {'collection': 'shops', 'indexes': ['slug']}

    name = StringField(required=True)
    company = StringField(required=True)
    site = StringField(required=True)
    slug = StringField(required=True)
