import pymongo
from scrapy_rotated_cookies.extensions import default_settings


class CookieMongoDBStorage(object):
    def __init__(self, settings):
        host_key = 'COOKIE_MONGODB_HOST'
        port_key = 'COOKIE_MONGODB_PORT'
        auth_db_key = 'COOKIE_MONGODB_AUTH_DB'
        username_key = 'COOKIE_MONGODB_USERNAME'
        password_key = 'COOKIE_MONGODB_PASSWORD'
        db_key = 'COOKIE_MONGODB_DB'
        coll_key = 'COOKIE_MONGODB_COLL'
        query_condition_key = 'COOKIE_QUERY_CONDITION'

        self.query_condition = settings.get(query_condition_key,
                                            getattr(default_settings, query_condition_key))
        self._uri = 'mongodb://{authentication}{host}:{port}/{auth_db}'.format(
            authentication='{username}:{password}@'.format(
                username=settings.get(username_key,
                                      getattr(default_settings, username_key)),
                password=settings.get(password_key,
                                      getattr(default_settings, password_key))
            ) if settings.get(username_key,
                              getattr(default_settings, username_key)) else '',
            host=settings.get(host_key, getattr(default_settings, host_key)),
            port=settings.get(port_key, getattr(default_settings, port_key)),
            auth_db=settings.get(auth_db_key,
                                 getattr(default_settings, auth_db_key))
        )
        self._client = pymongo.MongoClient(self._uri)
        self._db = self._client[
            settings.get(db_key, getattr(default_settings, db_key))]
        self._coll = self._db[
            settings.get(coll_key, getattr(default_settings, coll_key))]

    def retrieve_cookies(self):
        for cookie_item in self._coll.find(**self.query_condition):
            yield cookie_item
