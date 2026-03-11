from django.urls import path
from .views import MenuViewSet, CategoriesView
# from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('category', CategoriesView.as_view()),
    path('menu-item/<int:pk>', MenuViewSet.as_view({"get": "retrieve"})),
    path('menu-item', MenuViewSet.as_view({"get": "list", "post":"create"})),
    
]