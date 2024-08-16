from .feeds import LatestPostsFeed
from django.contrib.auth import views as auth_views
from .views import SellerListView, SellerDetailView, add_to_cart, cart_detail
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views


router = DefaultRouter()
router.register(r'products', views.ProductViewSet)

app_name = 'marketplace'
urlpatterns = [
    path('api/', include(router.urls)),
    path('', views.product_list1, name='product_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('buy/<int:id>/', views.buy_product, name='buy_product'),
    path('<int:product_id>/share/', views.product_share, name='product_share'),
    path('<int:product_id>/comment/', views.product_comment, name='product_comment'),
    path('tag/<slug:tag_slug>/', views.product_list1, name='product_list_by_tag'),
    path('feed/', LatestPostsFeed(), name='product_feed'),
    path('search/', views.product_search, name='product_search'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('sellers/', SellerListView.as_view(), name='seller_list'),
    path('seller/<str:username>/', SellerDetailView.as_view(), name='seller_detail'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart_detail, name='cart_detail'),
]