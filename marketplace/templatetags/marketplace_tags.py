from django import template
from marketplace.models import Product
from django.db.models import Count
import markdown
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def total_products():
    return Product.published.count()


@register.inclusion_tag('marketplace/product/latest_products.html')
def show_latest_products(count=5):
    latest_products = Product.published.order_by('-publish')[:count]
    return {'latest_products': latest_products}


@register.simple_tag
def get_most_commented_products(count=5):
    return Product.published.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments')[:count]


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))