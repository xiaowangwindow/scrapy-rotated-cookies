
import logging

from twisted.internet import task

from scrapy.exceptions import NotConfigured
from scrapy import signals

logger = logging.getLogger(__name__)


class LogStats(object):
    """Log basic scraping stats periodically"""

    def __init__(self, stats, interval=60.0):
        self.stats = stats
        self.interval = interval
        self.multiplier = 60.0 / self.interval
        self.task = None

    @classmethod
    def from_crawler(cls, crawler):
        interval = crawler.settings.getfloat('LOGSTATS_INTERVAL')
        if not interval:
            raise NotConfigured
        o = cls(crawler.stats, interval)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o

    def spider_opened(self, spider):
        self.pagesprev = 0
        self.itemsprev = 0

        self.task = task.LoopingCall(self.log, spider)
        self.task.start(self.interval)

    def log(self, spider):
        items = self.stats.get_value('item_scraped_count', 0)
        pages = self.stats.get_value('response_received_count', 0)
        irate = (items - self.itemsprev) * self.multiplier
        prate = (pages - self.pagesprev) * self.multiplier
        self.pagesprev, self.itemsprev = pages, items

        total_cookies = self.stats.get_value('rotated_cookie/total_cookie', 0)
        use_limit_cookies = self.stats.get_value('rotated_cookie/use_limit_cookie', 0)
        no_login_cookies = self.stats.get_value('rotated_cookie/no_login_cookie', 0)
        bad_cookies = self.stats.get_value('rotated_cookie/bad_cookies', 0)
        active_restrict_cookies = self.stats.get_value('rotated_cookie/active_restrict_cookies', 0)

        msg = ("Crawled %(pages)d pages (at %(pagerate)d pages/min), "
               "scraped %(items)d items (at %(itemrate)d items/min)\n"
               "total_cookies: %(total_cookies)d use_limit_cookies: %(use_limit_cookies)d "
               "no_login_cookies: %(no_login_cookies)d bad_cookies: %(bad_cookies)d active_restrict_cookies: %(active_restrict_cookies)d")
        log_args = {'pages': pages, 'pagerate': prate,
                    'items': items, 'itemrate': irate,
                    'total_cookies': total_cookies, 'use_limit_cookies': use_limit_cookies,
                    'no_login_cookies': no_login_cookies, 'bad_cookies': bad_cookies,
                    'active_restrict_cookies': active_restrict_cookies}
        logger.info(msg, log_args, extra={'spider': spider})

    def spider_closed(self, spider, reason):
        if self.task and self.task.running:
            self.task.stop()
