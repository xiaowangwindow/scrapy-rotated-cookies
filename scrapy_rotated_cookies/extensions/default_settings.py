
# DOWNLOADER_MIDDLEWARES.update({
#     'scrapy_rotated_cookies.downloadmiddlewares.rotated_cookies.RotatedCookiesMiddleware': 731,
# })
#
# EXTENSIONS.update({
#     'scrapy.extensions.logstats.LogStats': None,
#     'scrapy_rotated_cookies.extensions.logstats.LogStats': 731,
# })


COOKIE_STORAGE = 'scrapy_rotated_cookies.extensions.mongodb_storage.CookieMongoDBStorage'
COOKIE_MONGODB_HOST = '127.0.0.1'
COOKIE_MONGODB_PORT = 27017
COOKIE_MONGODB_AUTH_DB = 'admin'
COOKIE_MONGODB_USERNAME = ''
COOKIE_MONGODB_PASSWORD = ''
COOKIE_MONGODB_DB = ''
COOKIE_MONGODB_COLL = ''

COOKIE_ACTIVE_RESTRICT_NUM = 2500
COOKIE_QUERY_CONDITION = {
    'filter': {}
}

# COOKIE_STORAGE = 'scrapy_rotated_cookies.extensions.file_storage.CookieFileStorage'
#
# COOKIE_FILE_PATH = None
# ROTATED_COOKIES = []
