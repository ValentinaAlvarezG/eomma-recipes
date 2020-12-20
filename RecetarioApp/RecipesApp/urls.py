from django.urls import include, path
from RecipesApp import views

urlpatterns = [
    path('', views.home, name='home'),

    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),

    path('ingredients/', views.ingredients, name='ingredients'), 
    path('new_ingredient', views.add_ingredient, name='add_ingredient'),
    path('edit_ingredient/<int:ingredient_id>/', views.edit_ingredient, name='edit_ingredient'),
    path('delete_ingredient/<int:ingredient_id>/', views.delete_ingredient, name='delete_ingredient'),

    path('recipes/', views.recipes, name='recipes'),  
    path('new_recipe', views.add_recipe, name='add_recipe'),
    path('show_recipe/<int:recipe_id>/', views.show_recipe, name='show_recipe'),
    path('edit_recipe/<int:recipe_id>/', views.edit_recipe, name='edit_recipe'),
    path('delete_recipe/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),

    path('add_recipe_ingredient/<int:recipe_id>/', views.add_recipe_ingredient, name='add_recipe_ingredient'),
    path('edit_recipe_ingredient/<int:recipe_id>/<int:ingredient_id>/', views.edit_recipe_ingredient, name='edit_recipe_ingredient'),
    path('delete_recipe_ingredient/<int:recipe_id>/<int:ingredient_id>/', views.delete_recipe_ingredient, name='delete_recipe_ingredient'),
]
