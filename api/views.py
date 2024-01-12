from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


from .models import MenuItem, MenuItem
from api.serializers import MenuItemSerializer, MenuItemSerializer

import config.settings as config


# Validation
from django.forms import ValidationError

# Type hinting
from django.contrib.auth.models import User
from django.db.models import Model
from rest_framework.serializers import ModelSerializer
from django.http import HttpRequest


# Function based views

# Helper Function (services, modularity)
# for items
def is_group_has_permission(user: User, group_name: str) -> bool:
    """Check if user is in the specified group or is a staff member."""
    return any((user.groups.filter(name=group_name).exists(), user.is_staff))

def get_list_of_item(model_item: Model, model_item_serializer: ModelSerializer) -> Response:
    """Get a list of items. Method: GET"""
    items = model_item.objects.all()
    serializer = model_item_serializer(items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

def create_new_item(request: HttpRequest, model_item_serializer: ModelSerializer) -> Response:
    """Create a new item. Method: POST"""
    # TODO: handle duplication request data name (if Model title/name is already in database == data=request.data return that items already exist )
    # TODO: or handling all issue is unnessary, because it takes more time to deploy project/product to production? (in REST APIs development, is that RESTfull? what is RESTfull)
    try:
        # TODO: this type hinting is necessary? - serializer: ModelSerializer
        serializer: ModelSerializer = model_item_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "error_message": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )


# for single item
def retrieve_item(model_item, model_item_serializer: ModelSerializer) -> Response:
    """__summary_descriptions__. Method: GET"""
    serializer = model_item_serializer(model_item)
    return Response(serializer.data, status=status.HTTP_200_OK)

# TODO: input - request.data, using - request_data versus input - request, using - request.data
# TODO: type hinting for model_item and request params 
def update_item(model_item, request, model_item_serializer: ModelSerializer) -> Response:
    """__summary_descriptions__. Method: PUT"""
    serializer = model_item_serializer(model_item, data=request.data)
    # TODO: if serializer.is_valid(): versus serializer.is_valid(raise_exception=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def partial_update_item(model_item, request, model_item_serializer: ModelSerializer) -> Response:
    """__summary_descriptions__. Method: PATCH"""
    serializer = model_item_serializer(model_item, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def destroy_item(model_item) -> Response:
    """__summary_descriptions__. Method: DELETE"""
    model_item.delete()
    return Response(
        {"status_code": 204, "error_message": "Item Successfully deleted."},
        status=status.HTTP_204_NO_CONTENT
    )


# Category views
@api_view(['GET', 'POST'])
def categories(request):
    if request.method == 'GET':
        return get_list_of_item(model_item=MenuItem, model_item_serializer=MenuItemSerializer)
    
    # Check Permissions for POST
    if not is_group_has_permission(user=request.user, group_name=config.MANAGER_GROUP_NAME):
        return Response(
            {"status_code": status.HTTP_403_FORBIDDEN, "error_message": "Unauthorized - Permission Denied."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'POST':
        return create_new_item(request=request, model_item_serializer=MenuItemSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def single_category(request, item_id=None):
    # Try to retrieve data by item_id in model
    try:
        category_item = get_object_or_404(MenuItem, pk=item_id)
    except MenuItem.DoesNotExist:
        return Response(
            {"status_code": status.HTTP_404_NOT_FOUND, "error_message": "Resource Not Found or Does Not Exist."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        # TODO: variable - category_item or/versus just item and argument of function params - model_item or/versus just item
        return retrieve_item(model_item=category_item, model_item_serializer=MenuItemSerializer)
    
    # Check Permissions for PUT, PATCH, DELETE
    if not is_group_has_permission(user=request.user, group_name=config.MANAGER_GROUP_NAME):
            return Response(
                {"status_code": status.HTTP_403_FORBIDDEN, "error_message": "Unauthorized - Permission Denied."},
                status=status.HTTP_403_FORBIDDEN
            )
    
    if request.method == 'PUT':
        return update_item(model_item=category_item, request=request, model_item_serializer=MenuItemSerializer)
    elif request.method == 'PATCH':
        return partial_update_item(model_item=category_item, request=request, model_item_serializer=MenuItemSerializer)
    elif request.method == 'DELETE':
        return destroy_item(model_item=category_item)


# Menu-Item views
@api_view(['GET', 'POST'])
def menu_items(request):
    if request.method == 'GET':
        return get_list_of_item(model_item=MenuItem, model_item_serializer=MenuItemSerializer)
    
    # Check Permissions for POST
    if not is_group_has_permission(user=request.user, group_name=config.MANAGER_GROUP_NAME):
        return Response(
            {"status_code": status.HTTP_403_FORBIDDEN, "error_message": "Unauthorized - Permission Denied."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'POST':
        return create_new_item(request=request, model_item_serializer=MenuItemSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def single_menu_item(request, item_id=None):
    # Try to retrieve data by item_id in model
    try:
        menu_item = get_object_or_404(MenuItem, pk=item_id)
    except MenuItem.DoesNotExist:
        return Response(
            {"status_code": status.HTTP_404_NOT_FOUND, "error_message": "Resource Not Found or Does Not Exist."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        # TODO: variable - category_item or/versus just item and argument of function params - model_item or/versus just item
        return retrieve_item(model_item=menu_item, model_item_serializer=MenuItemSerializer)
    
    # Check Permissions for PUT, PATCH, DELETE
    if not is_group_has_permission(user=request.user, group_name=config.MANAGER_GROUP_NAME):
            return Response(
                {"status_code": status.HTTP_403_FORBIDDEN, "error_message": "Unauthorized - Permission Denied."},
                status=status.HTTP_403_FORBIDDEN
            )
    
    if request.method == 'PUT':
        return update_item(model_item=menu_item, request=request, model_item_serializer=MenuItemSerializer)
    elif request.method == 'PATCH':
        return partial_update_item(model_item=menu_item, request=request, model_item_serializer=MenuItemSerializer)
    elif request.method == 'DELETE':
        return destroy_item(model_item=menu_item)


# Testing
@api_view()
def check_permission_view(request):
    manager = request.user.groups.filter(name='Manager').exists()
    delivery = request.user.groups.filter(name='Delivery crew').exists()
    admin = request.user.is_staff
    
    if manager:
        return Response({"message": "Manager panel"})
    elif delivery:
        return Response({"message": "Delivery panel"})
    elif admin:
        return Response({"message": "Admin panel"})
    else:
        return Response({"message": "You are Customer"})
