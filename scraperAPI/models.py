from django.db import models

class My_Products(models.Model):
    product_name = models.CharField(max_length=120,blank=True,null=True)
    product_link = models.CharField(max_length=120,blank=True,null=True)
    product_sku = models.CharField(max_length=120,blank=True,null=True)
    product_Price = models.CharField(max_length =120,blank=True,null=True)
    # product_name = models.CharField(max_length=120,blank=True,null=True)
    
    def __str__(self):
        return self.product_name