from django.urls import path
from .views import MenuViewSet, ManagerGroupViewSet, DeliveryGroupViewSet, CartViewSet, UserViewSet, OrderViewSet
# from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('users/me', UserViewSet.as_view({"get": "list"})),
    path('menu-item/<int:pk>', MenuViewSet.as_view({"get": "retrieve", "put":"update", "patch":"partial_update", "delete":"destroy"})),
    path('menu-item', MenuViewSet.as_view({"get": "list", "post":"create"})),
    path('cart/menu-items', CartViewSet.as_view({"get": "list", "post":"create", "delete":"destroy"})),
    path('orders', OrderViewSet.as_view({"get": "list", "post": "create"})),
    path('orders/<int:pk>', OrderViewSet.as_view({"get": "retrieve", "post": "create", "patch": "partial_update", "delete":"destroy"})),
    path('groups/manager/users', ManagerGroupViewSet.as_view({"get": "list", "post":"create"})),
    path('groups/manager/users/<int:pk>', ManagerGroupViewSet.as_view({"delete":"destroy"})),
    path('groups/delivery-crew/users', DeliveryGroupViewSet.as_view({"get": "list", "post":"create"})),
    path('groups/delivery-crew/users/<int:pk>', DeliveryGroupViewSet.as_view({"delete":"destroy"})),
]