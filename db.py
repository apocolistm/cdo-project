from mongoengine import connect


def init_db(config):
    db = connect(
        db=config.DB,
        username=config.USER,
        password=config.PASSWORD,
        host=config.HOST,
        port=config.PORT,
        authentication_source=config.AUTH_DB,
    )
    return db
