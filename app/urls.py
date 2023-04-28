from django.urls import path
from app import views

urlpatterns = [
    path('', views.index, name="home"),
    path('run/', views.run_recipe, name="run_recipe"),
]