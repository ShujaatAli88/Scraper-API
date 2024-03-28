from django.contrib import admin
from .models import My_Products

class Products_info(admin.ModelAdmin):
    list_display=["product_name","product_sku"]

admin.site.register(My_Products,Products_info)