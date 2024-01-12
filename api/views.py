from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


from .models import Category, MenuItem
from api.serializers import CategorySerializer, MenuItemSerializer

from django.conf import settings


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
def is_group_has_permission(request: HttpRequest, group_name: str) -> bool:
    """Check if user is in the specified group or is a staff member."""
    return any((request.user.groups.filter(name=group_name).exists(), request.user.is_staff))


def get_list_of_item(Model: Model, ModelSerializer: ModelSerializer) -> Response:
    """Get a list of items. Method: GET"""
    items = Model.objects.all()
    serializer = ModelSerializer(items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

def create_new_item(request: HttpRequest, ModelSerializer: ModelSerializer) -> Response:
    """Create a new item. Method: POST"""
    serializer = ModelSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "error_message": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

def handle_items_view(request: HttpRequest, Model: Model, ModelSerializeer: ModelSerializer):
    """Handle views for a list of items and create new item. Method: GET, POST"""
    if request.method == 'GET':
        return get_list_of_item(Model=Model, ModelSerializer=ModelSerializeer)
    
    # Check Permissions for POST
    if not is_group_has_permission(request=request, group_name=settings.MANAGER_GROUP_NAME):
        return Response(
            {"status_code": status.HTTP_403_FORBIDDEN, "error_message": "Unauthorized - Permission Denied."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'POST':
        return create_new_item(request=request, ModelSerializer=ModelSerializeer)


# for single item
def retrieve_item(item: Model, ModelSerializer: ModelSerializer) -> Response:
    """Retrieve details for a single item. Method: GET"""
    serializer = ModelSerializer(item)
    return Response(serializer.data, status=status.HTTP_200_OK)

def update_full_item(request: HttpRequest, item: Model, ModelSerializer: ModelSerializer) -> Response:
    """Update an existing item. Method: PUT"""
    serializer = ModelSerializer(item, data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    except ValidationError as e:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "error_message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


def partial_update_item(request: HttpRequest, item: Model, ModelSerializer: ModelSerializer) -> Response:
    """Partially update an existing item. Method: PATCH"""
    serializer = ModelSerializer(item, data=request.data, partial=True)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "error_message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

def destroy_item(item: Model) -> Response:
    """Delete an existing item. Method: DELETE"""
    item.delete()
    return Response(
        {"status_code": status.HTTP_204_NO_CONTENT, "error_message": "Item Successfully deleted."},
        status=status.HTTP_204_NO_CONTENT
    )

def handle_item_views(request: HttpRequest, item_id, Model: Model, ModelSerializeer: ModelSerializer):
    """Handle views for a single item and manipulate item. Method: GET, PUT, PATCH, DELETE"""
    try:
        item = get_object_or_404(Model, pk=item_id)
    except Model.DoesNotExist as e:
        return Response(
            {"status_code": status.HTTP_404_NOT_FOUND, "error_message": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        return retrieve_item(item=item, ModelSerializer=ModelSerializeer)
    
    # Check Permissions for PUT, PATCH, DELETE
    if not is_group_has_permission(request=request, group_name=settings.MANAGER_GROUP_NAME):
            return Response(
                {"status_code": status.HTTP_403_FORBIDDEN, "error_message": "Unauthorized - Permission Denied."},
                status=status.HTTP_403_FORBIDDEN
            )
    
    if request.method == 'PUT':
        return update_full_item(request=request, item=item, ModelSerializer=ModelSerializeer)
    elif request.method == 'PATCH':
        return partial_update_item(request=request, item=item, ModelSerializer=ModelSerializeer)
    elif request.method == 'DELETE':
        return destroy_item(item=item)


# Category views
@api_view(['GET', 'POST'])
def categories(request):
    return handle_items_view(request=request, Model=Category, ModelSerializeer=CategorySerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def single_category(request, item_id=None):
    return handle_item_views(request=request, item_id=item_id, Model=Category, ModelSerializeer=CategorySerializer)


# MenuItem views
@api_view(['GET', 'POST'])
def menu_items(request):
    return handle_items_view(request=request, Model=MenuItem, ModelSerializeer=MenuItemSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def single_menu_item(request, item_id=None):
    return handle_item_views(request=request, item_id=item_id, Model=MenuItem, ModelSerializeer=MenuItemSerializer)
