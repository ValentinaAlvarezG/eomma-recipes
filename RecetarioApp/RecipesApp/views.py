from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from RecipesApp.models import *

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html', {})

# --------------------------- User --------------------------
def register(request):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    context = {'form': form}
    return render(request, 'register.html', context)

def login_user(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

    return render(request, 'login.html', {})

@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('login')



# --------------------------- Ingredients --------------------------
@login_required(login_url='login')
def ingredients(request):
    current_user = request.user
    user_ingredients = Ingredient.objects.filter(user__username=current_user.username)
    context = {'user_ingredients': user_ingredients}
    return render(request, 'ingredients.html', context)

@login_required(login_url='login')
def add_ingredient(request):
    units = MeasurementUnit.objects.all()
    context = {'units': units}

    if request.method == "POST":
        name, price, measurement_unit, user = get_ingredient_values(request)
        
        if validate_ingredient(name, price, user, measurement_unit):
            ingredient = Ingredient(name=name, price_per_unit=price, measurement_unit=measurement_unit, user=user)
            ingredient.save()
            return redirect('ingredients')

    return render(request, 'add_ingredient.html', context)

@login_required(login_url='login')
def edit_ingredient(request, ingredient_id):
    ingredient = Ingredient.objects.get(pk=ingredient_id)
    units = MeasurementUnit.objects.all()
    context = {'ingredient': ingredient, 'units': units}
    if request.method == "POST":
        name, price, measurement_unit, user = get_ingredient_values(request)
        
        if validate_ingredient(name, price, user, measurement_unit):
            ingredient.name = name
            ingredient.price_per_unit = price
            ingredient.measurement_unit = measurement_unit
            ingredient.save()
            return redirect('ingredients')
    return render(request, 'edit_ingredient.html', context)

def get_ingredient_values(request):
    # get values from form
    name = request.POST.get('name')
    price = request.POST.get('price')
    label = request.POST['unit']
    measurement_unit = MeasurementUnit.objects.filter(label=label)[0]
    user = request.user

    if price == '':
        price = 0
    return name, price, measurement_unit, user

def validate_ingredient(name, price, user, measurement_unit):
    validate_name = (name is not None) and (name != '')
    validate_price = (price is not None)
    validate_user = (user is not None)
    validate_unit = measurement_unit is not None
    validate = validate_name and validate_price and validate_unit and validate_user
    return validate
  

@login_required(login_url='login')
def delete_ingredient(request, ingredient_id):
    if request.method == "POST":
        Ingredient.objects.get(pk=ingredient_id).delete()
        return redirect('ingredients')

    return render(request, 'ingredients.html', {})


# --------------------------- Recipes --------------------------
@login_required(login_url='login')
def recipes(request):
    current_user = request.user
    user_recipes = Recipe.objects.filter(user__username=current_user.username)
    recipes = {} # {name: {object: RecipeObject, ingredients: [ {ingrediente_name: '', cantidad: '', unidad: ''}, ...], price: price }  }

    for recipe in user_recipes:
        price = calculate_price(recipe)
        name = recipe.name
        recipes[name] = {}
        recipes[name]['object'] = recipe
        recipes[name]['ingredients'] = []
        recipes[name]['price'] = price
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe.id)
        for recipe_ingredient in recipe_ingredients:
            ingredient_name = recipe_ingredient.ingredient.name
            qty = recipe_ingredient.qty
            measurement = recipe_ingredient.measurement
            recipes[name]['ingredients'].append({'ingredient_name': ingredient_name,'qty': qty, 'measurement': measurement})

    context = {'recipes_ingredients': recipes, 'user_recipes': user_recipes}
    return render(request, 'recipes.html', context)

def calculate_price(recipe):
    result = 0
    
    recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe.id)
    
    for recipe_ingredient in recipe_ingredients:
        ingredient = recipe_ingredient.ingredient

        # Get measurement unit (kg)
        measurement_unit = ingredient.measurement_unit
        # Get price per unit (2000)
        price_per_unit = ingredient.price_per_unit
        # Get measurement in recipe (gr)
        measurement = recipe_ingredient.measurement

        # Find measurement equivalence (0,001)
        equivalence = Equivalence.objects.get(measurement=measurement, measurement_unit=measurement_unit).equivalence 
        # Get qty
        qty = recipe_ingredient.qty
        
        ponderated_price = qty * equivalence * price_per_unit
        result += ponderated_price

    return result

@login_required(login_url='login')
def show_recipe(request, recipe_id):
    recipe = Recipe.objects.get(pk=recipe_id)
    print(recipe.name)
    recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe.id)
    print(recipe_ingredients)
    price = calculate_price(recipe)

    context = {'recipe': recipe, 'recipe_ingredients': recipe_ingredients, 'price': price}
    return render(request, 'show_recipe.html', context)

@login_required(login_url='login')
def add_recipe(request):

    if request.method == "POST":
        name = request.POST.get('name')
        portions = request.POST.get('portions')
        user = request.user
        
        if name is not None and portions is not None:
            recipe = Recipe(name=name, portions=portions, user=user)
            recipe.save()
            return redirect('add_recipe_ingredient', recipe.id)

    return render(request, 'add_recipe.html', {})

@login_required(login_url='login')
def edit_recipe(request, recipe_id):
    recipe = Recipe.objects.get(pk=recipe_id)
    context = {'recipe': recipe}
    if request.method == "POST":
        name = request.POST.get('name')
        portions = request.POST.get('portions')
        
        if name is not None and portions is not None:
            recipe.name = name
            recipe.portions = portions
            recipe.save()
            return redirect('show_recipe', recipe.id)

    return render(request, 'edit_recipe.html', context)

@login_required(login_url='login')
def delete_recipe(request, recipe_id):
    if request.method == "POST":
        Recipe.objects.get(pk=recipe_id).delete()
        return redirect('recipes')

    return render(request, 'recipes.html', {})


# --------------------------- Recipes Ingredients --------------------------
@login_required(login_url='login')
def add_recipe_ingredient(request, recipe_id):
    all_ingredients = Ingredient.objects.all()
    measurements = Equivalence.objects.all()
    recipe = Recipe.objects.get(pk=recipe_id)
    recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe.id)

    recipe_ingredients_names = []
    for recipe_ingredient in recipe_ingredients:
        recipe_ingredients_names.append(recipe_ingredient.ingredient.name)

    context = {'recipe': recipe, 
                'measurements': measurements, 
                'recipe_ingredients': recipe_ingredients, 
                'all_ingredients': all_ingredients,
                'recipe_ingredients_names': recipe_ingredients_names}

    
    if request.method == "POST":
        ingredient_name =  request.POST['ingredient']

        ingredient = Ingredient.objects.get(name=ingredient_name)
        recipe = Recipe.objects.get(pk=recipe_id)
        qty = request.POST.get('qty')
        measurement = request.POST['measurement']

        if ingredient is not None and recipe is not None and qty is not None and measurement is not None:
            relation = RecipeIngredient(ingredient=ingredient, recipe=recipe, qty=qty, measurement=measurement)
            relation.save()
            return redirect('add_recipe_ingredient', recipe.id)


    return render(request, 'add_recipe_ingredient.html', context)

# Edit particular ingredient from recipe
@login_required(login_url='login')
def edit_recipe_ingredient(request, recipe_id, ingredient_id):
    recipe = Recipe.objects.get(pk=recipe_id)
    ingredient = Ingredient.objects.get(pk=ingredient_id)
    recipe_ingredient = RecipeIngredient.objects.get(recipe=recipe, ingredient=ingredient)
    measurements = Equivalence.objects.all()
    context = {'recipe_ingredient': recipe_ingredient, 'measurements': measurements}
    
    if request.method == "POST":
        qty = request.POST.get('qty')
        measurement = request.POST['measurement']
        
        if qty is not None and measurement is not None:
            recipe_ingredient.qty = qty
            recipe_ingredient.measurement = measurement
            recipe_ingredient.save()
            return redirect('add_recipe_ingredient', recipe.id)

    return render(request, 'edit_recipe_ingredient.html', context)


@login_required(login_url='login')
def delete_recipe_ingredient(request, recipe_id, ingredient_id):
    if request.method == "POST":
        recipe = Recipe.objects.get(pk=recipe_id)
        ingredient = Ingredient.objects.get(pk=ingredient_id)
        recipe_ingredient = RecipeIngredient.objects.get(recipe=recipe, ingredient=ingredient).delete()
        return redirect('add_recipe_ingredient', recipe.id)

    return render(request, 'recipes.html', {})