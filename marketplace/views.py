from django.contrib.postgres.search import (
    TrigramSimilarity,
    SearchVector,
    SearchQuery,
    SearchRank)
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import CommentForm, EmailPostForm, SearchForm, UserRegistrationForm, UserEditForm, ProfileEditForm, LoginForm, RatingForm, SellerReviewForm
from .models import Product, Comment, Profile, Rating, SellerProfile, Cart, CartItem
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from taggit.models import Tag
from .tasks import send_notification_email, long_computation
from .serializers import ProductSerializer
from django.db.models import Q


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

def product_list1(request, tag_slug=None):
    product_list = Product.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        product_list = product_list.filter(tags__in=[tag])
    # Pagination with 3 posts per page
    paginator = Paginator(product_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer get the first page
        products = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range get last page of results
        products = paginator.page(paginator.num_pages)
    return render(
        request,
        'marketplace/product/list.html',
        {
            'products': products,
            'tag': tag,
            'page': products,
        }
    )


def product_detail(request, year, month, day, slug):
    product = get_object_or_404(
        Product,
        status=Product.Status.PUBLISHED,
        slug=slug,
        publish__year=year,
        publish__month=month,
        publish__day=day)

    average_rating = product.get_average_rating()
    comments = product.comments.filter(active=True)
    form = CommentForm()
    rating_form = None
    user_rating = None

    if request.user.is_authenticated:
        rating_form = RatingForm()
        try:
            user_rating = Rating.objects.get(product=product, user=request.user)
        except Rating.DoesNotExist:
            user_rating = None

        if request.method == 'POST' and 'rating' in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.user = request.user
                rating.product = product
                if user_rating:
                    user_rating.value = rating.value
                    user_rating.save()
                else:
                    rating.save()
                product.update_average_rating()
                return redirect('marketplace:product_detail', year=year, month=month, day=day, slug=slug)

    return render(
        request,
        'marketplace/product/detail.html',
        {
            'product': product,
            'comments': comments,
            'form': form,
            'rating_form': rating_form,
            'user_rating': user_rating,
            'average_rating': average_rating,
        }
    )

    comments = product.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()

    # # List of similar posts
    # product_tags_ids = product.tags.values_list('id', flat=True)
    # similar_products = Product.published.filter(
    #     tags__in=product_tags_ids
    # ).exclude(id=product.id)
    # similar_posts = similar_products.annotate(
    #     same_tags=Count('templatetags')
    # ).order_by('-same_tags', '-publish')[:4]

    return render(
        request,
        'marketplace/product/detail.html',
        {
            'product': product,
            'comments': comments,
            'form': form,
            # 'similar_products': similar_products,
        }
    )


class ProductListView(ListView):
    model = Product
    template_name = 'marketplace/product/list.html'
    context_object_name = 'products'
    paginate_by = 2

    def get_queryset(self):
        queryset = Product.published.all()
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags__in=[tag])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            context['tag'] = get_object_or_404(Tag, slug=tag_slug)
        else:
            context['tag'] = None
        return context


def product_share(request, product_id):
    product = get_object_or_404(Product, id=product_id, status=Product.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            product_url = request.build_absolute_uri(
                product.get_absolute_url()
            )
            subject = (
                f"{cd['name']} ({cd['email']}) "
                f"recommends you read {product.title}"
            )
            message = (f"Read {product.title} at {product_url}\n\n"
                       f"{cd['name']}\'s comments: {cd['comments']}"
                       )
            send_mail(
                subject=subject,
                message=message,
                from_email='nedilja90@gmail.com',
                recipient_list=[cd['to']]
            )
            sent = True
    else:
        form = EmailPostForm()

    return render(
        request,
        'marketplace/product/share.html',
        {'product': product,
         'form': form,
         'sent': sent
         }
    )


def buy_product(request, id):
    product = get_object_or_404(Product, id=id)
    return redirect('marketplace:product_list')


@require_POST
@login_required
def product_comment(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        status=Product.Status.PUBLISHED
    )
    comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.product = product        # Save the comment to the database
        comment.save()
    return render(
        request,
        'marketplace/product/comment.html',
        {
            'product': product,
            'form': form,
            'comment': comment
        },
    )


def product_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Product.published.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            ).order_by('-updated')

    return render(
        request,
        'marketplace/product/search.html',
        {
            'form': form,
            'query': query,
            'results': results
        },
    )


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password'],
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('marketplace:product_list')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required
def dashboard(request):
    return render(
        request,
        'account/dashboard.html',
        {'section': 'dashboard'}
    )


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(
                request,
                'registration/register_done.html',
                {'new_user': new_user},
            )
    else:
        user_form = UserRegistrationForm()
    return render(
        request,
        'registration/registration.html',
        {'user_form': user_form}
    )


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(
            instance=request.user,
            data=request.POST
        )
        profile_form = ProfileEditForm(
            instance=request.user.profile,
            data=request.POST,
            files=request.FILES,
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(
        request,
        'registration/edit.html',
        {
            'user_form': user_form,
            'profile_form': profile_form
        },
    )


class SellerListView(ListView):
    model = SellerProfile
    template_name = 'marketplace/sellers/seller_list.html'
    context_object_name = 'sellers'


class SellerDetailView(DetailView):
    model = SellerProfile
    template_name = 'marketplace/sellers/seller_detail.html'
    context_object_name = 'seller'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        seller = self.get_object()
        context['products'] = Product.objects.filter(seller=seller.user)
        context['review_form'] = SellerReviewForm()
        return context

    def post(self, request, *args, **kwargs):
        seller = self.get_object()
        review_form = SellerReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.seller = seller
            review.user = request.user
            review.save()
            return redirect(seller.get_absolute_url())
        return self.get(request, *args, **kwargs)


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('marketplace:cart_detail')


@login_required
def cart_detail(request):
    cart = get_object_or_404(Cart, user=request.user)
    total = cart.get_total()
    return render(request, 'marketplace/cart/detail_for_card.html', {'cart': cart, 'total': total})


def my_view(request):
    # Виклик асинхрон для відправки e-mail
    send_notification_email.delay('Subject', 'Message', ['recipient@example.com'])

    # Виклик асинхронного завдання для обчислення
    result = long_computation.delay(10, 20)

    return render(request, 'template.html', {'result': result})


