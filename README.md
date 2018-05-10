scrapy-rotated-cookies
========

# Overview
scrapy-rotated-cookies is a scrapy downloader middleware to attach cookies to Request cyclically.
Cookie list can be read from MongoDB, file or settings module. Besides, 

# Requirements
- Python 2.7 or Python3.4+
- Works on Linux, Windows, Mac OSX, BSD

# Install
The quick way:

```
pip install scrapy-rotated-cookie
```

# Documentation
In settings.py, for example:

```

# Common Setting
DOWNLOADER_MIDDLEWARES.update({
    'scrapy_rotated_cookies.downloadmiddlewares.rotated_cookies.RotatedCookiesMiddleware': 731,
})

EXTENSIONS.update({
    'scrapy.extensions.logstats.LogStats': None,
    'scrapy_rotated_cookies.extensions.logstats.LogStats': 731,
})
COOKIE_ACTIVE_RESTRICT_NUM = sys.maxsize
COOKIE_QUERY_CONDITION = {
    'filter': {},
    'projection': {},
}

# MongoDB Backend
COOKIE_STORAGE = 'scrapy_rotated_cookies.extensions.mongodb_storage.CookieMongoDBStorage'
COOKIE_MONGODB_USERNAME = 'username'
COOKIE_MONGODB_PASSWORD = 'password'
COOKIE_MONGODB_HOST = '127.0.0.1'
COOKIE_MONGODB_PORT = 27017
COOKIE_MONGODB_AUTH_DB = 'admin'
COOKIE_MONGODB_DB = 'db'
COOKIE_MONGODB_COLL = 'coll'

# File Backend
COOKIE_STORAGE = 'scrapy_rotated_cookies.extensions.file_storage.CookieFileStorage'
COOKIE_FILE_PATH = 'file_path'

# Settings Backend
COOKIE_STORAGE = 'scrapy_rotated_cookies.extensions.file_storage.CookieFileStorage'
COOKIE_FILE_PATH = None
ROTATED_COOKIES = []

```