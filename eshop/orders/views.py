import os
import weasyprint
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from cart.models import Cart
from user.models import UserProfile
from .models import OrderItem, Order
from .forms import OrderCreateForm
from .tasks import order_created
from shop.recommender import Recommender

recommender = Recommender()


@login_required
def order_create(request):
    cart = Cart(request)
    current_user = request.user
    profile = UserProfile.objects.get(user_id=current_user.id)
    purchased_products = []  # products bought list for recommender

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user  # linking an order to the current user

            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount

            order.save()

            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
                purchased_products.append(item['product'])

            recommender.products_bought(purchased_products)  # save purchased products for recommender

            cart.clear()

            order_created.delay(order.id)  # launch asynchronous task
            request.session['order_id'] = order.id  # set an order in a session

            return redirect(reverse('payment:process'))  # redirect to payment

        else:
            print(form.errors)
    else:
        form = OrderCreateForm()

    return render(request,
                  'create.html',
                  {'cart': cart, 'form': form, 'profile': profile})


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,
                  'detail.html',
                  {'order': order})


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('pdf.html',
                            {'order': order})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_{order.id}.pdf'
    css_path = os.path.join(settings.STATIC_ROOT, 'css/pdf.css')
    weasyprint.HTML(string=html).write_pdf(response,
                                           stylesheets=[weasyprint.CSS(filename=css_path)])
    return response
