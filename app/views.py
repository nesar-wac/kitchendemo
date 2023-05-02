import json

from django.shortcuts import render

from app.utils import process_recipes


def index(request):
    with open("app/recipes.json") as recipe_file:
        recipes_list = recipe_file.read()
        recipes = json.loads(recipes_list)
    return render(request, "index.html", {"recipes": recipes})


def run_recipe(request):
    recipe_id = int(request.GET["id"])
    target_recipes = []
    with open("app/recipes.json") as recipe_file:
        recipes_list = json.loads(recipe_file.read())
        for recipe in recipes_list:
            if recipe["id"] == recipe_id:
                target_recipes.append(recipe)
    process_recipes(target_recipes)
    return render(request, "index.html", {"status": "success"})
