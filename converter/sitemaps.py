from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            'converter:redirect',
            'converter:loading',
            'converter:home',
            'converter:result',
        ]

    def location(self, item):
        return reverse(item)
