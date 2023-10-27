from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='user_index'),
    path('update/', views.user_update, name='user_update'),
    path('password/', views.user_password, name='user_password'),
    path('orders/', views.user_orders, name='user_orders'),
    path('order_detail/<int:id>', views.user_order_detail, name='user_order_detail'),
    path('orders_product/', views.user_order_product, name='user_order_product'),
    path('order_product_detail/<int:id>/<int:oid>', views.user_order_product_detail, name='user_order_product_detail'),
    path('comments/', views.user_comments, name='user_comments'),
    path('delete_comment/<int:id>', views.user_delete_comment, name='user_delete_comment'),
]
