from django.contrib import admin
from .models import Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=('id', 'name', 'price', 'stock_quantity', 'category')
    list_filter=('category',)
    search_fields=('name','category')