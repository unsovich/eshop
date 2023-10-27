import admin_thumbnails
from django.contrib import admin

from .models import Category, ProductImage, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin_thumbnails.thumbnail('image')
class ProductImagesInline(admin.TabularInline):
    model = ProductImage
    readonly_fields = ('id',)
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['category', 'name', 'price', 'available', 'quantity', 'id', 'image_tag']
    list_filter = ['category', 'available']
    list_editable = ['available', 'price', 'quantity']
    readonly_fields = ('image_tag',)
    inlines = [ProductImagesInline,]
    prepopulated_fields = {'slug': ('name',)}
