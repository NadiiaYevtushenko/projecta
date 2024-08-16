from django.urls import reverse
from .models import Product, Cart, CartItem, Rating, Comment
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User



#Модульні тести
class ProductModelTest(TestCase):
    def setUp(self):
        # Створюємо користувача, який буде виступати як продавець
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Створюємо продукт із зазначенням продавця
        self.product = Product.objects.create(
            title='Test Product',
            slug='test-product',
            price=10.00,
            description='Test description',
            seller=self.user  # Вказуємо продавця
        )

    def test_str_method(self):
        self.assertEqual(str(self.product), 'Test Product')


class ProductRatingTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.product = Product.objects.create(
            title='Test Product',
            slug='test-product',
            price=10.00,
            description='Test description',
            seller=self.user  # Вказуємо продавця
        )

    def test_update_average_rating(self):
        Rating.objects.create(product=self.product, user=self.user, value=5)
        self.product.update_average_rating()
        self.assertEqual(self.product.get_average_rating(), 5.00)


#Функціональні тести
class ProductListViewTest(TestCase):

    def test_product_list_view_status_code(self):
        response = self.client.get(reverse('marketplace:product_list'))
        self.assertEqual(response.status_code, 200)


User = get_user_model()


class ProductDetailViewTest(TestCase):

    def setUp(self):
        # Створюємо користувача-продавця
        self.seller = User.objects.create_user(username='seller', password='12345')

        # Створюємо продукт з продавцем
        self.product = Product.objects.create(
            title='Test Product',
            slug='test-product',
            price=10.00,
            description='Test description',
            status=Product.Status.PUBLISHED,
            seller=self.seller  # Передаємо користувача як продавця
        )

    def test_product_detail_view(self):
        url = reverse('marketplace:product_detail',
                      args=[self.product.publish.year, self.product.publish.month, self.product.publish.day,
                            self.product.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Product')


#Інтеграційні тести
class ProductSearchTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='seller', password='testpass')

        self.product1 = Product.objects.create(
            title='Gaming Console',
            slug='gaming-console',
            price=400.00,
            description='Latest gaming console',
            status=Product.Status.PUBLISHED,
            seller=self.user,
        )

        self.product2 = Product.objects.create(
            title='Smartphone',
            slug='smartphone',
            price=800.00,
            description='Latest smartphone',
            status=Product.Status.PUBLISHED,
            seller=self.user,
        )

    def test_search_products(self):
        url = reverse('marketplace:product_search')
        response = self.client.get(url, {'query': 'smartphone'})
        self.assertEqual(response.status_code, 200)

        # Перевіряємо, що у відповідях є потрібний продукт
        self.assertContains(response, 'Smartphone')

        # Перевіряємо, що результати містять лише очікуваний продукт
        results = response.context['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, 'Smartphone')


class ProductCommentTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='buyer', password='testpass')
        self.seller = get_user_model().objects.create_user(username='seller', password='testpass')

        self.product = Product.objects.create(
            title='Bluetooth Speaker',
            slug='bluetooth-speaker',
            price=150.00,
            description='Portable Bluetooth Speaker',
            status=Product.Status.PUBLISHED,
            seller=self.seller,
        )

    def test_add_comment_to_product(self):
        self.client.login(username='buyer', password='testpass')
        url = reverse('marketplace:product_comment', kwargs={'product_id': self.product.id})
        response = self.client.post(url, {
            'name': 'John Doe',
            'email': 'john@example.com',
            'body': 'Great product!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Comment.objects.filter(product=self.product, name='John Doe', body='Great product!').exists())


# #Функціональні тести для REST API
class SimpleProductAPITest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='seller', password='testpass')
        self.client.login(username='seller', password='testpass')

        # Створюємо тестовий продукт
        self.product = Product.objects.create(
            title='Gaming Console',
            slug='gaming-console',
            price=400.00,
            description='Latest gaming console',
            status=Product.Status.PUBLISHED,
            seller=self.user,
        )

        self.url_list = reverse('marketplace:product-list')

    def test_get_product_list(self):
        # Отримуємо список продуктів
        response = self.client.get(self.url_list)

        # Перевіряємо, що відповідь успішна (200 OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Перевіряємо, що продукт з'являється у відповіді
        self.assertContains(response, 'Gaming Console')