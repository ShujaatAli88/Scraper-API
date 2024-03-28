from rest_framework import serializers
from .models import My_Products
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(many=True, queryset=My_Products.objects.all())
    owner = serializers.ReadOnlyField(source='owner.username')
    class Meta:
        model = User
        fields = ["id","username","owner"]
        


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = My_Products
        fields = ['product_name', 'product_link', 'product_sku','product_Price']