from django.urls import path
from .views import dashboard, serve_map

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('map/', serve_map, name='map'), 
]