from django.urls import path

from app import views

urlpatterns = [
    path("", views.index, name="home"),
    path("recipes/one/", views.get_one_recipe),
    path("recipes/all/", views.get_all_recipes),
]
