from django.contrib import admin
from django.urls import path, include
from ProjectA.sitemaps import PostSitemap
from django.contrib.sitemaps.views import sitemap

sitemaps = {'marketplace.products': PostSitemap}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('marketplace.urls', namespace='marketplace')),
    path('sitemap.xml',
         sitemap,
         {'sitemaps': sitemaps},
         name='django.contrib.sitemaps.views.sitemap'
         ),
]
