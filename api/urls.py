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
    # User group management endpoints
    path('groups/manager/users/', views.manage_manager_users),
    path('groups/manager/users/<int:user_id>/', views.manage_manager_user),
    path('groups/delivery-crew/users/', views.manage_delivery_crew_users),
    path('groups/delivery-crew/users/<int:user_id>/', views.manage_delivery_crew_user),
    # Cart management endpoints
    path('cart/menu-items', views.cart_items),
    # Order management endpoints
    path('orders/', views.orders),
    path('orders/<int:order_id>', views.order),
    
    
    # Testing
    path('groups/names/', views.get_group_name_mapping),
]