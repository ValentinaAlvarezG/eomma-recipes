from django.contrib import admin
from RecipesApp.models import *

admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)
admin.site.register(MeasurementUnit)
admin.site.register(Equivalence)