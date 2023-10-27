from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from orders.models import Order, OrderItem
from shop.models import Category, Comment
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import UserProfile


@login_required(login_url='/login')
def index(request):
    # return HttpResponse('User app page')
    category = Category.objects.all()
    current_user = request.user
    profile = UserProfile.objects.get(user_id=current_user.id)
    context = {'category': category, 'profile': profile}
    return render(request, 'user_profile.html', context)


def login_form(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')  # Redirect to a success page
        else:
            messages.warning(request, 'Login failed!')
            return HttpResponseRedirect('/login')

    category = Category.objects.all()
    context = {'category': category}
    return render(request, 'login_form.html', context)


def register_form(request):
    if request.method == 'POST':  # if user was sent data for the form
        form = RegisterForm(request.POST)  # create object of RegisterForm
        if form.is_valid():  # if data entered is valid
            form.save()  # create new user with entered data
            username = form.cleaned_data.get('username')  # get cleaned data
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)  # if auth is ok than login
            messages.success(request, 'Your account has been created!')
            current_user = request.user
            data = UserProfile()  # create user profile
            data.user_id = current_user.id
            data.save()  # save to DB
            return HttpResponseRedirect('/')
        else:
            messages.warning(request, form.errors)
            return HttpResponseRedirect('/register')
    else:  # if request method is not POST
        form = RegisterForm()
    category = Category.objects.all()
    context = {'category': category, 'form': form}
    return render(request, 'register_form.html', context)


def logout_func(request):
    logout(request)
    return HttpResponseRedirect('/')


@login_required(login_url='/login')
def user_update(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your account has been updated')
            return HttpResponseRedirect('/user')
    else:
        category = Category.objects.all()
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.userprofile)
        context = {
            'category': category,
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, 'user_update.html', context)


@login_required(login_url='/login')
def user_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return HttpResponseRedirect('/user')
        else:
            messages.error(request, 'Please correct the error below.<br>' + str(form.errors))
            return HttpResponseRedirect('/user/password')
    else:
        category = Category.objects.all()
        form = PasswordChangeForm(request.user)
        return render(request, 'user_password.html', {'form': form, 'category': category})


@login_required(login_url='/login')
def user_orders(request):
    current_user = request.user
    orders = Order.objects.filter(user_id=current_user.id)
    return render(request, 'user_orders.html', {'orders': orders})


@login_required(login_url='/login')
def user_order_detail(request, id):
    category = Category.objects.all()
    current_user = request.user
    order = Order.objects.get(user_id=current_user.id, id=id)
    order_items = OrderItem.objects.filter(order_id=id)
    context = {
        'category': category,
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'user_order_detail.html', context)


@login_required(login_url='/login')
def user_order_product(request):
    category = Category.objects.all()
    current_user = request.user
    order_product = OrderItem.objects.filter(user_id=current_user.id).order_by('-id')
    context = {'category': category, 'order_product': order_product}
    return render(request, 'user_order_products.html', context)


@login_required(login_url='/login')
def user_order_product_detail(request,id,oid):
    category = Category.objects.all()
    current_user = request.user
    order = Order.objects.get(user_id=current_user.id, id=oid)
    order_items = OrderItem.objects.filter(id=id, user_id=current_user.id)
    context = {
        'category': category,
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'user_order_detail.html', context)


def user_comments(request):
    category = Category.objects.all()
    current_user = request.user
    comments = Comment.objects.filter(user_id=current_user.id)
    context = {
        'category': category,
        'comments': comments,
    }
    return render(request, 'user_comments.html', context)


@login_required(login_url='/login')
def user_delete_comment(request, id):
    current_user = request.user
    Comment.objects.filter(id=id, user_id=current_user.id).delete()
    messages.success(request, 'Comment deleted.')
    return HttpResponseRedirect('/user/comments')
