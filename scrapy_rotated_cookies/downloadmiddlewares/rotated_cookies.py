import logging
from typing import AnyStr, Dict
from collections import defaultdict

from scrapy import Request, Spider, signals
from scrapy.crawler import Crawler
from scrapy.utils.misc import load_object

from .. import signals as cookies_signals
from ..extensions import default_settings

logger = logging.getLogger(__name__)


def convert_cookie_from_str(cookie_str: AnyStr) -> Dict:
    return dict(map(lambda cookie_item: cookie_item.split('=', maxsplit=1),
                    cookie_str.split(';')))


def extract_cookie(origin_cookie):
    if isinstance(origin_cookie, dict) and 'cookie' in origin_cookie:
        return origin_cookie.get('cookie')
    elif isinstance(origin_cookie, str):
        return convert_cookie_from_str(origin_cookie)
    elif isinstance(origin_cookie, (list, dict)):
        return origin_cookie


class CookieExhaustException(Exception):
    def __str__(self):
        return 'Run out of Cookie'


class RotatedCookiesMiddleware():
    USE_LIMIT_KEY = 'use_limit_cookies'
    NO_LOGIN_KEY = 'no_login_cookies'
    BAD_KEY = 'bad_cookies'
    ACTIVE_RESTRICT_KEY = 'active_restrict_cookies'

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        o = cls(crawler.settings, crawler.stats)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(o.account_use_limit,
                                signal=cookies_signals.cookie_use_limit)
        crawler.signals.connect(o.account_no_login,
                                signal=cookies_signals.cookie_no_login)
        crawler.signals.connect(o.account_bad,
                                signal=cookies_signals.cookie_bad)
        return o

    def __init__(self, settings, stats):
        self.stats = stats
        self.storage = load_object(settings['COOKIE_STORAGE'])(settings)
        self.active_restrict_num = settings.get(
            'COOKIE_ACTIVE_RESTRICT_NUM',
            getattr(default_settings, 'COOKIE_ACTIVE_RESTRICT_NUM')
        )
        self.cookies = list(self.storage.retrieve_cookies())
        self.valid_cookies = list()
        self.invalid_cookies_dict = defaultdict(list)
        self.cookies_stat = defaultdict(int)
        self.cookies_gen = self._gen_cookies()

    def spider_opened(self, spider: Spider):
        self.stats.set_value('rotated_cookie/total_cookie', len(self.cookies))

    def spider_closed(self, spider: Spider):
        self.stats.set_value('rotated_cookie/use_limit_cookie',
                             len(self.invalid_cookies_dict[
                                     self.USE_LIMIT_KEY]))
        self.stats.set_value('rotated_cookie/no_login_cookie',
                             len(self.invalid_cookies_dict[
                                     self.NO_LOGIN_KEY]))
        self.stats.set_value('rotated_cookie/bad_cookies',
                             len(self.invalid_cookies_dict[self.BAD_KEY]))
        self.stats.set_value('rotated_cookie/active_restrict_cookies',
                             len(self.invalid_cookies_dict[
                                     self.ACTIVE_RESTRICT_KEY]))

    def process_request(self, request: Request, spider: Spider):
        if request.meta.get('has_cookie', False):
            return None

        try:
            origin_cookie = next(self.cookies_gen)
        except CookieExhaustException as exc:
            logger.error(exc)
            spider.crawler.engine.close_spider(spider, str(exc))

        cookie = extract_cookie(origin_cookie)
        if not cookie:
            return request

        new_request = request.replace(cookies=cookie)
        new_request.meta.update({
            'has_cookie': True,
            'dont_redirect': True,
            'origin_cookie': origin_cookie,
        })
        if isinstance(origin_cookie, dict) and origin_cookie.get('proxy'):
            new_request.meta['proxy'] = origin_cookie.get('proxy')

        return new_request

    def _gen_cookies(self):
        while True:
            self.valid_cookies = [
                cookie for cookie in self.cookies if
                all(map(
                    lambda cookie_list: cookie not in cookie_list,
                    self.invalid_cookies_dict.values()
                ))
            ]

            if (not self.valid_cookies
                or len(self.valid_cookies) < len(self.cookies)/2):
                raise CookieExhaustException()

            for cookie in self.valid_cookies:
                if (self.stats.get_value(
                            'cookie_use_time/' + cookie.get('username'), 0
                ) > self.active_restrict_num):

                    self.invalid_cookies_dict[
                        self.ACTIVE_RESTRICT_KEY].append(cookie)
                    self.stats.set_value(
                        'rotated_cookie/active_restrict_cookies',
                        len(self.active_restrict_cookies)
                    )
                    continue
                else:
                    self.stats.inc_value(
                        'cookie_use_time/' + cookie.get('username'))
                    yield cookie

    def account_use_limit(self, request: Request):
        origin_cookie = request.meta.get('origin_cookie')
        logger.warning('cookie use limit: %s', origin_cookie)
        self.invalid_cookies_dict[self.USE_LIMIT_KEY].append(origin_cookie)
        self.stats.set_value('rotated_cookie/use_limit_cookie',
                             len(self.invalid_cookies_dict[self.USE_LIMIT_KEY]))

    def account_no_login(self, request: Request):
        origin_cookie = request.meta.get('origin_cookie')
        logger.warning('cookie no login: %s', origin_cookie)
        self.invalid_cookies_dict[self.NO_LOGIN_KEY].append(origin_cookie)
        self.stats.set_value('rotated_cookie/no_login_cookie',
                             len(self.invalid_cookies_dict[self.NO_LOGIN_KEY]))

    def account_bad(self, request: Request):
        origin_cookie = request.meta.get('origin_cookie')
        logger.warning('cookie bad: %s', origin_cookie)
        self.invalid_cookies_dict[self.BAD_KEY].append(origin_cookie)
        self.stats.set_value('rotated_cookie/bad_cookies',
                             len(self.invalid_cookies_dict[self.BAD_KEY]))
