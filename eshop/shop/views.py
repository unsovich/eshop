from django.shortcuts import render, get_object_or_404
from cart.forms import CartAddProductForm
from .forms import SearchForm
from .models import Category, Product
from .recommender import Recommender


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if request.method == 'POST':
        # Обработка запроса POST, отправленного из формы поиска
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            products = Product.objects.filter(name__icontains=query)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        # Получите все дочерние категории для данной категории (рекурсивный запрос)
        subcategories = Category.objects.filter(parent_category=category)
        # Включите продукты из выбранной категории и всех ее дочерних категорий
        products = products.filter(category__in=[category] + list(subcategories))

    context = {
        'category': category,
        'categories': categories,
        'products': products,
    }
    return render(request, 'product/list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(Product,
                                id=id,
                                slug=slug,
                                available=True)

    # Создайте форму для добавления в корзину
    cart_product_form = CartAddProductForm()

    r = Recommender()
    recommended_products = r.suggest_products_for([product], 4)

    return render(request,
                  'product/detail.html',
                  {'product': product,
                   'cart_product_form': cart_product_form,
                   'recommended_products': recommended_products})


def search(request):
    query = request.GET.get('query')
    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    context = {'products': products, 'query': query}
    return render(request, 'search_result.html', context)


def base(request):
    products_slider = Product.objects.all().order_by('id')[:4]  # first 4 products
    products_cheapest = Product.objects.all().order_by('price')[:4]  # cheapest 4 products
    products_latest = Product.objects.all().order_by('-id')[:4]  # last 4 products
    products_random = Product.objects.all().order_by('?')[:4]  # randomly selected
    page = 'base'
    context = {'page': page,
               'products_slider': products_slider,
               'products_cheapest': products_cheapest,
               'products_latest': products_latest,
               'products_random': products_random,
               }
    return render(request, 'base.html', context)
