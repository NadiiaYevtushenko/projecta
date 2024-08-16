from django.contrib import admin
from .models import Product, Comment


# admin.site.register(Product)
@admin.register(Product)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'price', 'seller', 'publish', 'status']
    list_filter = ['status', 'created', 'publish', 'seller']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ['seller']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']
    show_facets = admin.ShowFacets.ALWAYS


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'product', 'created', 'active']
    list_filter = ['active', 'created', 'updated']
    search_fields = ['name', 'email', 'body']
