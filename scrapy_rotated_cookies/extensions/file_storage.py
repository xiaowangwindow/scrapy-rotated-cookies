
from scrapy_rotated_cookies.extensions import default_settings

class CookieFileStorage():
    def __init__(self, settings):
        file_path_key = 'COOKIE_FILE_PATH'
        self.settings = settings
        self.file_path = settings.get(file_path_key, getattr(default_settings, file_path_key))

    def retrieve_cookies(self):
        if not self.file_path:
            return self.settings.get('ROTATED_COOKIES', [])
        else:
            return open(self.file_path).readlines()
