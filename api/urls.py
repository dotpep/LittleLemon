from django.urls import path, include
from . import views

urlpatterns = [
    # Function based
    # Category endpoints
    path('category/', views.categories, name='list of categories and create new category'),
    path('category/<int:item_id>/', views.single_category, name='retrive single category by item_id, and manipulate'),
    # Menu-Items endpoints
    path('menu-items/', views.menu_items, name='list of menu items and create new menu item'),
    path('menu-items/<int:item_id>/', views.single_menu_item, name='retrive single category by item_id, and manipulate'),
    
    # Testing
    path('manager-view/', views.check_permission_view),
]