from django.contrib.sitemaps import Sitemap
from marketplace.models import Product


class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return Product.published.all()

    def lastmod(self, obj):
        return obj.updated