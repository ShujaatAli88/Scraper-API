from django.urls import path
from . import views

urlpatterns = [
    path('get_products/', views.GETProducts.as_view(),name='get_products'), #Scraper API
    path('products/<int:product_quantity>/',views.ProductList.as_view(),name='from_database'),    #Get Database Products
    path('product/<int:pk>/',views.SingleProduct.as_view(),name='my_product'), #Get Single Product based on Id..
    path('search/<str:sku>/', views.Search_With_Sku.as_view(), name='search_product'),
    path('pagination/',views.MyPaginator.as_view(), name = 'my_paginator'),
]
