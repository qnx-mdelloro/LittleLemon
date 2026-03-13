from rest_framework import serializers
from django.contrib.auth.models import User, Group
from .models import MenuItem, Category, Cart, Order, OrderItem

# Django Model Serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

# User-defined Model S
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title']
class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only=True)
    category = CategorySerializer(read_only=True) 
    class Meta:
        model = MenuItem
        fields = ['id','title','price','inventory', 'category', 'category_id']
class CartSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    class Meta:
        model = Cart
        fields = ['id', 'user_id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']

class OrderSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(read_only=True)
    delivery_crew_id = serializers.IntegerField(write_only=True, allow_null=True)
    delivery_crew = UserSerializer(read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user_id', 'user', 'delivery_crew_id', 'delivery_crew', 'status', 'total', 'date']
class OrderItemSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(write_only=True)
    order = OrderSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'order_id', 'order', 'menuitem', 'quantity', 'unit_price', 'price']