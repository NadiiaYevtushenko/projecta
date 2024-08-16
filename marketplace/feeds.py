import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy

from .models import Product


class LatestPostsFeed(Feed):
    title = 'My marketplace'
    link = reverse_lazy('marketplace:product_list')
    description = 'New products of my marketplace.'

    def items(self):
        return Product.published.all()[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return truncatewords_html(markdown.markdown(item.description), 30)

    def item_pubdate(self, item):
        return item.publish