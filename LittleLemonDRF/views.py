# Python Imports
from urllib3 import request

# Django Imports
from django.forms import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group

# DRF Imports
from rest_framework import generics, viewsets, status
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

class MenuViewSet(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication, TokenAuthentication, SessionAuthentication]
    def get_permissions(self):
        # check the action and return the permission class accordingly
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return []
    
    def list(self, request):
        queryset = MenuItem.objects.all()
        serializer = MenuItemSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = MenuItem.objects.all()
        menu_item = get_object_or_404(queryset, pk=pk)
        serializer = MenuItemSerializer(menu_item)
        return Response(serializer.data)
    
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
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
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
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

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
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        user = User.objects.get(id=request.user.id)
        if(user.groups.filter(name='Manager').exists()):
            queryset = MenuItem.objects.all()
            menu_item = get_object_or_404(queryset, pk=pk)
            
            menu_item.delete()
            return Response({'message': 'Item deleted successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

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
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
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
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        requester = User.objects.get(id=request.user.id)
        if(requester.groups.filter(name='Manager').exists()):
            user = get_object_or_404(User, id=pk)
            managers = Group.objects.get(name='Manager')
            managers.user_set.remove(user)
            return Response({'message': 'Item deleted successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
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
            users = User.objects.filter(groups__name='Delivery Staff')
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['post'])
    def create(self, request):
        requester = User.objects.get(id=request.user.id)
        if(requester.groups.filter(name='Manager').exists()):
            username = request.data.get('username')
            if(username):
                user = get_object_or_404(User, username=username)
                managers = Group.objects.get(name='Delivery Staff')
                managers.user_set.add(user)
                return Response({'status': 'Delivery Staff added successfully'}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        requester = User.objects.get(id=request.user.id)
        if(requester.groups.filter(name='Manager').exists()):
            user = get_object_or_404(User, id=pk)
            managers = Group.objects.get(name='Delivery Staff')
            managers.user_set.remove(user)
            return Response({'message': 'Delivery Staff removed successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

class CartViewSet(viewsets.ViewSet):
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
        user = User.objects.get(id=request.user.id)
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['delete'])
    def destroy(self, request, pk=None):
        user = User.objects.get(id=request.user.id)
        if(user.groups.filter(name='Manager').exists()):
            queryset = MenuItem.objects.all()
            menu_item = get_object_or_404(queryset, pk=pk)
            
            menu_item.delete()
            return Response({'message': 'Item deleted successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
