from django.db import models
from django.contrib import admin
from RecipesApp.models import *
from django.contrib.auth.models import User
# Create your models here.
class MeasurementUnit(models.Model):
    label = models.CharField(max_length=100)

    def __str__(self):
      return f'MeasurementUnit {self.id}: {self.label}'

class Equivalence(models.Model):
    measurement = models.CharField(max_length=100, null=False)
    equivalence = models.FloatField(null=False)
    measurement_unit = models.ForeignKey(MeasurementUnit, on_delete=models.CASCADE, null=False)

    def __str__(self):
      return f'Equivalence {self.id}: 1 {self.measurement} equivale a {self.equivalence} {self.measurement_unit}'

class Ingredient(models.Model):
    name = models.CharField(max_length=100, null=False)
    measurement_unit = models.ForeignKey(MeasurementUnit, on_delete=models.CASCADE, null=False)
    price_per_unit = models.FloatField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
      return f'Ingredient {self.id}: {self.name}'

class Recipe(models.Model):
    name = models.CharField(max_length=100, null=False)
    portions = models.FloatField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')

    def __str__(self):
      return f'Recipe {self.id}: {self.name}'

class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, null=False)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=False)
    qty = models.FloatField(null=False)
    measurement = models.CharField(max_length=30, null=False)

    def __str__(self):
      return f'RecipeIngredient {self.id}: {self.recipe.name} - {self.ingredient.name}'


