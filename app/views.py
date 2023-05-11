import json
from django.shortcuts import render
from app.utils import run_recipes


def index(request):
    with open("app/recipes.json") as recipe_file:
        recipes_list = recipe_file.read()
        recipes = json.loads(recipes_list)
    return render(request, "index.html", {"recipes": recipes})


def get_one_recipe(request):
    recipe_id = int(request.GET["id"])
    target_recipe = []
    with open("app/recipes.json") as recipe_file:
        recipes_list = json.loads(recipe_file.read())
        for recipe in recipes_list:
            if recipe["id"] == recipe_id:
                target_recipe.append(recipe)
    run_recipes(target_recipe)
    return render(request, "index.html", {"status": "success"})


def get_all_recipes(request):
    with open("app/recipes.json") as recipe_file:
        recipes_list = json.loads(recipe_file.read())
        run_recipes(recipes_list)
    return render(request, "index.html", {"status": "success"})
