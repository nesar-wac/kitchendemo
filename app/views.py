import json
from django.shortcuts import render


def index(request):
    with open('app/recipes.json') as recipe_file:
        recipes_list = recipe_file.read()
        recipes = json.loads(recipes_list)
    return render(request, "index.html", {"recipes": recipes})


def run_recipe(request):
    print("it is working")
    return render(request, "index.html", {"status": "success"})
