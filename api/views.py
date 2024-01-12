from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


from .models import Category, MenuItem
from .serializers import CategorySerializer, MenuItemSerializer, UserSerializer
from django.contrib.auth.models import User, Group

from django.conf import settings


# Validation
from django.forms import ValidationError

# for Custom class Permission
from rest_framework.permissions import BasePermission

# Type hinting
from django.contrib.auth.models import User
from django.db.models import Model
from rest_framework.serializers import ModelSerializer
from django.http import HttpRequest


# Helper Function for Category and MenuItem views
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
        {"status_code": status.HTTP_204_NO_CONTENT, "message": "Item Successfully deleted."},
        status=status.HTTP_204_NO_CONTENT
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


def handle_item_views(request: HttpRequest, item_id, Model: Model, ModelSerializeer: ModelSerializer):
    """Handle views for a single item and manipulate item. Method: GET, PUT, PATCH, DELETE"""
    try:
        parsed_item = get_object_or_404(Model, pk=item_id)
    except Model.DoesNotExist as e:
        return Response(
            {"status_code": status.HTTP_404_NOT_FOUND, "error_message": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        return retrieve_item(item=parsed_item, ModelSerializer=ModelSerializeer)
    
    # Check Permissions for PUT, PATCH, DELETE
    if not is_group_has_permission(request=request, group_name=settings.MANAGER_GROUP_NAME):
            return Response(
                {"status_code": status.HTTP_403_FORBIDDEN, "error_message": "Unauthorized - Permission Denied."},
                status=status.HTTP_403_FORBIDDEN
            )
    
    if request.method == 'PUT':
        return update_full_item(request=request, item=parsed_item, ModelSerializer=ModelSerializeer)
    elif request.method == 'PATCH':
        return partial_update_item(request=request, item=parsed_item, ModelSerializer=ModelSerializeer)
    elif request.method == 'DELETE':
        return destroy_item(item=parsed_item)


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


# User group management

# Custom class Permission for Manager and Delivery Crew groups
class IsGroupManager(BasePermission):
    """
    Allows access only to Authenticated users with Manager Group/Role Permissions.
    """
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and any((
            request.user.is_staff, 
            request.user.groups.filter(name=settings.MANAGER_GROUP_NAME).exists()
        ))

class IsGroupDeliveryCrew(BasePermission):
    """
    Allows access only to Authenticated users with Delivery Crew Group/Role Permissions.
    """
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and any((
            request.user.is_staff, 
            request.user.groups.filter(name=settings.DELIVERY_CREW_GROUP_NAME).exists()
        ))


# Helper Function for User group management
def get_users_in_group(group_name: str) -> Response:
    """Get a list of users belonging to the specified group. Method: GET"""
    users = User.objects.filter(groups__name=group_name)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

def assign_user_to_group(user: User, group: Group, group_name: settings) -> Response:
    """Assign the given user to the specified group. Method: POST"""
    if not user.groups.filter(name=group_name).exists():
        group.user_set.add(user)
        return Response(
            {"status_code": status.HTTP_201_CREATED, "message": f"{user.username}, Was Successfully Added to {group_name} group."}, 
            status=status.HTTP_201_CREATED
        )
    return Response(
        {"status_code": status.HTTP_400_BAD_REQUEST,"error_message": f"{user.username} User Is Already {group_name}."}, 
        status=status.HTTP_400_BAD_REQUEST
    )

def remove_user_from_group(user: User, group: Group, group_name: str) -> Response:
    """Remove the specified user from the specified group using the user's ID. Method: DELETE"""
    if user.groups.filter(name=group_name).exists():
        group.user_set.remove(user)
        return Response(
            {"status_code": status.HTTP_200_OK, "message": f"{user.username}, Was Successfully Deleted from {group_name} group."}, 
            status=status.HTTP_200_OK
        )
    return Response(
        {"status_code": status.HTTP_400_BAD_REQUEST,"error_message": f"{user.username} User Is Not {group_name}."}, 
        status=status.HTTP_400_BAD_REQUEST
    )

def assign_or_remove_user_from_group(request: HttpRequest, group_name: str, action: str) -> Response:
    """Assign or remove a user from the specified group based on the action parameter. Action: assign for POST, remove for DELETE"""
    try:
        username = request.data['username']
        group = Group.objects.get(name=group_name)
        user = get_object_or_404(User, username=username)
    except KeyError as e:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "message": {"error_message": str(e).replace("'", ""), "username": "This field is required."}}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    if action == 'assign':
        return assign_user_to_group(user=user, group=group, group_name=group_name)
    elif action == 'remove':
        return remove_user_from_group(user=user, group=group, group_name=group_name)
    else:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "error_message": "Invalid action."},
            status=status.HTTP_400_BAD_REQUEST
        )


def handle_users_management_views(request: HttpRequest, group_name: settings):
    """Handle views for a user management actions for a group. Method: GET, POST, DELETE"""
    if request.method == 'GET':
        return get_users_in_group(group_name=group_name)
    elif request.method == 'POST':
        return assign_or_remove_user_from_group(request=request, group_name=group_name, action='assign')
    elif request.method == 'DELETE':
        return assign_or_remove_user_from_group(request=request, group_name=group_name, action='remove')


# TODO: type hinting for user_id
def handle_user_management_views(request: HttpRequest, user_id, group_name: settings):
    """Handle views for a user management actions for a single user in a group. Method: DELETE"""
    if request.method == 'DELETE':
        return remove_user_from_group(user_id=user_id, group_name=group_name)


# TODO: refactor naming convension for functions, variable
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsGroupManager])
def manage_manager_users(request):
    return handle_users_management_views(request=request, group_name=settings.MANAGER_GROUP_NAME)

@api_view(['DELETE'])
@permission_classes([IsGroupManager])
def manage_manager_user(request, user_id):
    return handle_user_management_views(request=request, user_id=user_id, group_name=settings.MANAGER_GROUP_NAME)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsGroupManager])
def manage_delivery_crew_users(request):
    return handle_users_management_views(request=request, group_name=settings.DELIVERY_CREW_GROUP_NAME)

@api_view(['DELETE'])
@permission_classes([IsGroupManager])
def manage_delivery_crew_user(request, user_id):
    return handle_user_management_views(request=request, user_id=user_id, group_name=settings.DELIVERY_CREW_GROUP_NAME)




# Testing
def get_group_names() -> list:
    return list(Group.objects.values_list('name', flat=True))

# Get the group names dynamically from the database
GROUP_NAMES = get_group_names()

GROUP_NAME_MAPPING = {group.lower(): group for group in GROUP_NAMES}

def get_actual_group_name(logical_group_name: str) -> str:
    return GROUP_NAME_MAPPING.get(logical_group_name.lower(), logical_group_name)


GROUP_NAME_MAPPING = {
    'manager': settings.MANAGER_GROUP_NAME,
    'delivery_crew': settings.DELIVERY_CREW_GROUP_NAME,
}


@api_view(['GET'])
def get_group_name_mapping(request):
    return Response({
        "list": GROUP_NAMES, 
        "get_delivery_crew": get_actual_group_name('delivery_crew'),
        "get_manager": get_actual_group_name('manager')
    })