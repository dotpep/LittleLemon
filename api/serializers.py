from rest_framework import serializers

from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User, Group
from django.conf import settings


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug']


# TODO: Add validation POST request for price, stock fields
class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'groups']


class CartSerializer(serializers.ModelSerializer):
    # TODO: Implement of depth foreign key relations to retrieve title and etc fields not only id because its clearify what is fields actually save
    #user = UserSerializer(read_only=True)
    #menuitem = MenuItemSerializer(read_only=True)
    #menuitem_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    #user = UserSerializer(read_only=True)
    #delivery_crew = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'delivery_crew', 'date', 'total']
        
        
class OrderItemSerializer(serializers.ModelSerializer):
    #order = OrderSerializer(read_only=True)
    #menuitem = MenuItemSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']
