# Python Imports
from urllib3 import request
import datetime

# Django Imports
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
#from django_filters.rest_framework import DjangoFilterBackend
# DRF Imports
from rest_framework import generics, viewsets, status, filters
from rest_framework.decorators import permission_classes, action
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Local Imports
from .serializers import MenuItemSerializer, CategorySerializer, CartSerializer, OrderSerializer, OrderItemSerializer, GroupSerializer, UserSerializer
from .models import MenuItem, Category, Cart, Order, OrderItem

class UserViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication, TokenAuthentication, SessionAuthentication]
    def get_permissions(self):
        # check the action and return the permission class accordingly
        if self.action in ['list']:
            return [IsAuthenticated()]
        return []
    def list(self, request):
        
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

class MenuViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication, TokenAuthentication, SessionAuthentication]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['id', 'price', 'inventory']
    ordering = ['id']
    # ordering_fields = ['price', 'inventory']
    
    #filter_backends = [DjangoFilterBackend]
    #filter_fields = ['title', 'category__title']
    def get_permissions(self):
        # check the action and return the permission class accordingly
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return []
    def get_queryset(self):
        queryset = MenuItem.objects.all()
        title = self.request.query_params.get('title')
        category = self.request.query_params.get('category')
        ordering = self.request.query_params.get('ordering')
        if title is not None:
            queryset = queryset.filter(title__contains=title)
        if category is not None:
            queryset = queryset.filter(category__title__contains=category)
        if ordering is not None:
            ordering_fields = [field.strip() for field in ordering.split(',')]
            queryset = queryset.order_by(*ordering_fields)
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        serializer = MenuItemSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        queryset = MenuItem.objects.all()
        menu_item = get_object_or_404(queryset, pk=pk)
        serializer = MenuItemSerializer(menu_item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def create(self, request):
        # Alternative JWT Authentication
        # access_token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        # token = AccessToken(access_token)
        # user_id = token.payload['user_id']
        user = User.objects.get(id=request.user.id)
        if(user.groups.filter(name='Manager').exists()):
            serializer = MenuItemSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)
    @action(detail=True, methods=['put'])
    def update(self, request, pk=None):
        user = User.objects.get(id=request.user.id)
        if(user.groups.filter(name='Manager').exists()):
            queryset = MenuItem.objects.all()
            menu_item = get_object_or_404(queryset, pk=pk)

            serializer = MenuItemSerializer(menu_item, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=True, methods=['patch'])
    def partial_update(self, request, pk=None):
        user = User.objects.get(id=request.user.id)
        if(user.groups.filter(name='Manager').exists()):
            queryset = MenuItem.objects.all()
            menu_item = get_object_or_404(queryset, pk=pk)

            serializer = MenuItemSerializer(menu_item, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        user = User.objects.get(id=request.user.id)
        if(user.groups.filter(name='Manager').exists()):
            queryset = MenuItem.objects.all()
            menu_item = get_object_or_404(queryset, pk=pk)
            
            menu_item.delete()
            return Response({'message': 'Menu Item deleted successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)

# Manager Management Views

class ManagerGroupViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication, TokenAuthentication, SessionAuthentication]
    def get_permissions(self):
        # check the action and return the permission class accordingly
        
        if self.action in ['list', 'create', 'destroy']:
            return [IsAuthenticated()]
        return []
    
    def list(self, request):
        requester = User.objects.get(id=request.user.id)
        if(requester.groups.filter(name='Manager').exists()):
            users = User.objects.filter(groups__name='Manager')
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=True, methods=['post'])
    def create(self, request):
        requester = User.objects.get(id=request.user.id)
        if(requester.groups.filter(name='Manager').exists()):
            username = request.data.get('username')
            if(username):
                user = get_object_or_404(User, username=username)
                managers = Group.objects.get(name='Manager')
                managers.user_set.add(user)
                return Response({'status': 'Manager added successfully'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        requester = User.objects.get(id=request.user.id)
        if(requester.groups.filter(name='Manager').exists()):
            user = get_object_or_404(User, id=pk)
            managers = Group.objects.get(name='Manager')
            managers.user_set.remove(user)
            return Response({'message': 'Manager removed successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)
    
class DeliveryGroupViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication, TokenAuthentication, SessionAuthentication]
    
    def get_permissions(self):
        # check the action and return the permission class accordingly
        
        if self.action in ['list', 'create', 'destroy']:
            return [IsAuthenticated()]
        return []
    
    def list(self, request):
        requester = User.objects.get(id=request.user.id)
        if(requester.groups.filter(name='Manager').exists()):
            users = User.objects.filter(groups__name='Delivery Crew')
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=True, methods=['post'])
    def create(self, request):
        requester = User.objects.get(id=request.user.id)
        if(requester.groups.filter(name='Manager').exists()):
            username = request.data.get('username')
            if(username):
                user = get_object_or_404(User, username=username)
                managers = Group.objects.get(name='Delivery Crew')
                managers.user_set.add(user)
                return Response({'status': 'Delivery Crew added successfully'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        requester = User.objects.get(id=request.user.id)
        if(requester.groups.filter(name='Manager').exists()):
            user = get_object_or_404(User, id=pk)
            managers = Group.objects.get(name='Delivery Crew')
            managers.user_set.remove(user)
            return Response({'message': 'Delivery Crew removed successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)

class CartViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication, TokenAuthentication, SessionAuthentication]
    def get_permissions(self):
        # check the action and return the permission class accordingly
        if self.action in ['list', 'create', 'destroy']:
            return [IsAuthenticated()]
        return []
    def list(self, request):
        queryset = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create(self, request):
        # Alternative JWT Authentication
        # access_token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        # token = AccessToken(access_token)
        # user_id = token.payload['user_id']
        user = get_object_or_404(User, id=request.user.id)
        menu_item = get_object_or_404(MenuItem, id=request.data.get('menuitem_id'))
        menu_item_serialized = MenuItemSerializer(menu_item)
        
        cart = request.data.copy()
        cart['user_id'] = request.user.id
        cart['unit_price'] = menu_item_serialized.data.get('price')
        cart['price'] = float(cart['quantity']) * float(cart['unit_price'])
        serializer = CartSerializer(data=cart)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        cart = Cart.objects.filter(user=request.user).delete()
        return Response({'message': 'Cart cleared successfully'}, status=status.HTTP_200_OK)
        #return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

class OrderViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication, TokenAuthentication, SessionAuthentication]
    def get_permissions(self):
        # check the action and return the permission class accordingly
        if self.action in ['list', 'create', 'destroy']:
            return [IsAuthenticated()]
        return []
    
    def get_queryset(self, queryset):
        if queryset is None:
            queryset = OrderItem.objects.all()
        title = self.request.query_params.get('title')
        category = self.request.query_params.get('category')
        ordering = self.request.query_params.get('ordering')
        if title is not None:
            queryset = queryset.filter(title__contains=title)
        if category is not None:
            queryset = queryset.filter(category__title__contains=category)
        if ordering is not None:
            ordering_fields = [field.strip() for field in ordering.split(',')]
            queryset = queryset.order_by(*ordering_fields)
        return queryset
    
    @action(detail=True, methods=['get'])
    def list(self, request):
        user = get_object_or_404(User, id=request.user.id)
        if(user.groups.filter(name='Manager').exists()):
            queryset = self.get_queryset(None)
            serializer = OrderItemSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif(user.groups.filter(name='Delivery Crew').exists()):
            queryset = OrderItem.objects.filter(order__delivery_crew=user)
            queryset = self.get_queryset(queryset)
            serializer = OrderItemSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            queryset = OrderItem.objects.filter(order__user=user)
            queryset = self.get_queryset(queryset)
            serializer = OrderItemSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['get'])
    def retrieve(self, request, pk=None):
        user = get_object_or_404(User, id=request.user.id)
        user_serializer = UserSerializer(user)
        order = get_object_or_404(Order, id=pk)
        order_serializer = OrderSerializer(order)
        if order_serializer.data['user'] != user_serializer.data:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        order_items = OrderItem.objects.filter(order=order)
        order_items_serializer = OrderItemSerializer(order_items, many=True)
        return Response(order_items_serializer.data)

    @action(detail=True, methods=['post'])
    def create(self, request):
        # Create Order Object
        user = get_object_or_404(User, id=request.user.id)
        initial_order_data = {
            'user_id': request.user.id,
            'delivery_crew_id': None,
            'date': datetime.date.today().strftime("%Y-%m-%d"),
            'total': 0
        }
        order_serializer = OrderSerializer(data=initial_order_data)
        order_serializer.is_valid(raise_exception=True)
        order_serializer.save()
        order_id = order_serializer.data['id']
        
        # Create Order Item Object Per Cart Item
        subtotal = 0
        cart = Cart.objects.filter(user=user)
        cart_serializer = CartSerializer(cart, many=True)
        for cart_item in cart_serializer.data:
            order_item_data = {
                'order_id': order_id,
                'menuitem_id': cart_item['menuitem']['id'],
                'quantity': cart_item['quantity'],
                'unit_price': cart_item['unit_price'],
                'price': cart_item['price']
            }
            order_item_serializer = OrderItemSerializer(data=order_item_data)
            order_item_serializer.is_valid()
            order_item_serializer.save()
            subtotal += float(cart_item['price'])
        
        # Update Order Total
        order = get_object_or_404(Order, id=order_id)
        order_serializer = OrderSerializer(order, data={'total': subtotal}, partial=True)
        order_serializer.is_valid()
        order_serializer.save()
        
        cart = Cart.objects.filter(user=user).delete()
        
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)
        #return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['patch'])
    def partial_update(self, request, pk=None):
        user = get_object_or_404(User, id=request.user.id)
        
        if(user.groups.filter(name='Manager').exists()):
            queryset = Order.objects.filter(id=pk)
            order = get_object_or_404(queryset, pk=pk)
            cleaned_data = {}
            if(len(request.data) > 2):
                return Response(status=status.HTTP_403_FORBIDDEN)
            if('delivery_crew_id' in request.data):
                cleaned_data['delivery_crew_id'] = request.data['delivery_crew_id']
            if('status' in request.data):
                cleaned_data['status'] = request.data['status']
            
            serializer = OrderSerializer(order, data=cleaned_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif(user.groups.filter(name='Delivery Crew').exists()):
            queryset = Order.objects.filter(id=pk)
            order = get_object_or_404(queryset, pk=pk)
            cleaned_data = {}
            if('status' in request.data and len(request.data) == 1):
                cleaned_data['status'] = request.data['status']
            
            serializer = OrderSerializer(order, data=cleaned_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        user = get_object_or_404(User, id=request.user.id)
        if(user.groups.filter(name='Manager').exists()):
            order = Order.objects.filter(id=pk).delete()
            return Response({'message': 'Order deleted successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_401_UNAUTHORIZED)

