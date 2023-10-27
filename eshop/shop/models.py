import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg, Count
from django.forms import ModelForm
from django.urls import reverse
from django.utils.safestring import mark_safe


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200,
                            unique=True)
    parent_category = models.ForeignKey('self',
                                        null=True,
                                        blank=True,
                                        on_delete=models.SET_NULL,
                                        related_name='subcategories')

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'], )]
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category',
                       args=[self.slug])


def product_image_filename(instance, filename):
    ext = filename.split('.')[-1]  # get the file extension
    unique_id = uuid.uuid4().hex[:5]  # generate the unique identifier (5 symbols)
    return f'img/products/{instance.name}_{unique_id}.{ext}'


class Product(models.Model):
    VARIANTS = (
        ('None', 'None'),
        ('Size', 'Size'),
        ('Color', 'Color'),
        ('Color+Size', 'Color+Size'),
    )

    category = models.ForeignKey(Category,
                                 related_name='products',
                                 on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    image = models.ImageField(upload_to=product_image_filename,
                              blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10,
                                decimal_places=2)
    available = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField(default=0)
    variant = models.CharField(max_length=10,
                               choices=VARIANTS,
                               default='None')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]

    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src={} height="50"/>'.format(self.image.url))
        else:
            return ''

    def average_review(self):
        reviews = Comment.objects.filter(product=self, status='Checked').aggregate(average=Avg('rate'))
        average = 0
        if reviews['average'] is not None:
            average = float(reviews['average'])

        return average

    def count_review(self):
        reviews = Comment.objects.filter(product=self, status='Checked').aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])

        return count

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                       args=[self.id, self.slug])


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    name = models.CharField(max_length=30, blank=True)
    image = models.ImageField(upload_to='img/products/', blank=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name = 'images'
        verbose_name_plural = 'images'

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=7,
                            blank=True,
                            null=True)

    def __str__(self):
        return self.name

    def color_tag(self):
        if self.code is not None:
            return mark_safe('<p style="background-color:{}">Color</p>'.format(self.code))
        else:
            return ''


class Size(models.Model):
    name = models.CharField(max_length=10,
                            unique=True)

    def __str__(self):
        return self.name


class Comment(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Checked', 'Checked'),
        ('Spam', 'Spam'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, blank=True)
    comment = models.CharField(max_length=250, blank=True)
    rate = models.IntegerField(default=1)
    ip = models.CharField(max_length=20, blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['subject', 'comment', 'rate']
