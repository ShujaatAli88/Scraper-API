from django.shortcuts import render
from django.views import generic
from .models import My_Products
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from rest_framework.views import APIView
from . serializers import ProductSerializer
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from selenium.webdriver import Chrome
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from django.core.paginator import Paginator
from rest_framework import permissions
from scraperAPI.permissions import IsOwnerOrReadOnly


class GETProducts(generic.ListView):
    template_name = 'get_products.html' 
    context_object_name = 'products'

    def get_queryset(self):
        driver = webdriver.Chrome()
        url = "https://www.darbydental.com/Home.aspx"
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "loginLink"))).click()
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "ctl00$logonControl$txtUsername")))
        user_name = driver.find_element(By.NAME, "ctl00$logonControl$txtUsername")
        password = driver.find_element(By.NAME, "ctl00$logonControl$txtPassword")
        user_name.send_keys("alex@joinordo.com")
        password.send_keys("corp80216")
        driver.find_element(By.NAME, "ctl00$logonControl$btnLogin").click()
        sleep(5)
        driver.find_element(By.CLASS_NAME, "menu-bar").click()
        all_catagories = driver.find_elements(By.CLASS_NAME, "bigcathover")
        
        products = []
        for catagory in all_catagories:
            ignore_exceptions = (NoSuchElementException,StaleElementReferenceException)
            catagory = WebDriverWait(driver, 20, ignored_exceptions=ignore_exceptions).until(EC.presence_of_element_located((By.ID,"divbars")))
            cat_link = catagory.get_attribute('href')
            next_catagory = urljoin(url, cat_link)
            driver.get(next_catagory)
            sleep(2)  #sleep for 2 seconds
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            product_names = soup.find_all('div', class_="prod-title")
            product_skus = soup.find_all('label', class_="prodno")
            all_products = soup.find_all('div', class_="card-body")
            prices = soup.find_all('div', class_="prod-price")
        
            for product_name, prod_sku, product_link, prod_price in zip(product_names, product_skus, all_products, prices):
                a_tags = product_link.find('a')
                href_value_of_product = a_tags['href']
                price = prod_price.text
                new_price = price.replace('1 @ ', '')
                products.append({'name': product_name.text,
                                  "sku": prod_sku.text,
                                  "Product_detail_link": urljoin(url, href_value_of_product),
                                  "Product_Price": new_price})
        
        for product_data in products:
            My_Products.objects.create(product_name=product_data['name'],
                                       product_link=product_data['Product_detail_link'],
                                       product_sku=product_data['sku'],
                                       product_Price=product_data["Product_Price"])
        
        return products


class Search_With_Sku(APIView):
    
    def get(self,request,sku):
        sku = self.kwargs['sku']
        driver = webdriver.Chrome()
        base_url = "https://www.darbydental.com/Home.aspx"
        driver.get(base_url)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "loginLink"))).click()
        user_name = driver.find_element(By.NAME, "ctl00$logonControl$txtUsername")
        password = driver.find_element(By.NAME, "ctl00$logonControl$txtPassword")
        user_name.send_keys("alex@joinordo.com")
        password.send_keys("corp80216")
        driver.find_element(By.NAME, "ctl00$logonControl$btnLogin").click()
        sleep(4)
        search_bar = driver.find_element(By.NAME,"ctl00$bigSearchTerm")
        search_bar.send_keys(sku)
        driver.find_element(By.NAME,"ctl00$btnBigSearch").click()
        sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_name = soup.find('div', class_="prod-title")
        product_sku = soup.find('label', class_="prodno")
        my_product = soup.find('div', class_="card-body")
        a_tag = my_product.find('a')
        link_of_product = a_tag['href']
        prices = soup.find('div', class_="prod-price")
        price = prices.text
        new_price = price.replace('1 @ ', '')
        
        products = []
        products.append({
            "name" : product_name.text,
            "sku":product_sku.text,
            "Product_detail_link":urljoin(base_url,link_of_product),
            "price" : new_price
        })
        
        my_sku = My_Products.objects.filter(product_sku=sku).first()
        if my_sku:
            my_product = products[0]  #getting the first Element in the list...
            my_sku.product_name = my_product["name"]
            my_sku.product_link = my_product["Product_detail_link"]
            my_sku.product_sku = my_product['sku']
            my_sku.product_Price = my_product["price"]
            my_sku.save()
            
        return Response(products)

#API For Getting Data From The Database:
class ProductList(APIView):
    [permissions.IsAuthenticatedOrReadOnly,
                      IsOwnerOrReadOnly]    
    def perform_create(self, serializer):
      serializer.save(owner=self.request.user)
      
    def get(self, request,product_quantity):
        products = My_Products.objects.all()
        pk = self.kwargs['product_quantity']    
        paginator = Paginator(products, pk)
        page_number = request.query_params.get('page')          
        page_obj = paginator.get_page(page_number)          
        serializer = ProductSerializer(page_obj, many=True)
        return Response({"Here are The Requested Number of Products: ":serializer.data}, status=status.HTTP_200_OK)

#get The Data of a Specific Product for Provided product
class SingleProduct(APIView):
    
    def get(self,request,pk):
        product = My_Products.objects.get(id=pk)
        serializer = ProductSerializer(product)
        return Response({"The Product for The Provided Id is:":serializer.data},status=status.HTTP_200_OK)


#Pagination Using Djangor's Paginator Class....
class MyPaginator(APIView):
    
    def get(self, request):
        products = My_Products.objects.all()
        paginator = Paginator(products, 2)
        page_number = request.query_params.get('page')
        page_obj = paginator.get_page(page_number)
        my_data = ProductSerializer(page_obj, many=True)
        
        return Response(my_data.data)