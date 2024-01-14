from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import datetime


from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from django.contrib.auth.models import User, Group

from django.conf import settings


# Validation
from django.forms import ValidationError
from decimal import Decimal, InvalidOperation

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
    user = request.user
    return any((user.groups.filter(name=group_name).exists(), user.is_staff))


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
        {"status_code": status.HTTP_204_NO_CONTENT, "detail": "Item Successfully deleted."},
        status=status.HTTP_204_NO_CONTENT
    )


def handle_items(request: HttpRequest, Model: Model, ModelSerializeer: ModelSerializer) -> Response:
    """Handle views for a list of items and create new item. Method: GET, POST"""
    if request.method == 'GET':
        return get_list_of_item(Model=Model, ModelSerializer=ModelSerializeer)
    
    # Check Permissions for POST
    if not is_group_has_permission(request=request, group_name=settings.MANAGER_GROUP_NAME):
        return Response(
            {"status_code": status.HTTP_403_FORBIDDEN, "error_message": "Permission Denied."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'POST':
        return create_new_item(request=request, ModelSerializer=ModelSerializeer)
    else:
        return Response({"detail": "Invalid method for this endpoint."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def handle_item(request: HttpRequest, item_id: int, Model: Model, ModelSerializeer: ModelSerializer) -> Response:
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
                {"status_code": status.HTTP_403_FORBIDDEN, "error_message": "Permission Denied."},
                status=status.HTTP_403_FORBIDDEN
            )
    
    if request.method == 'PUT':
        return update_full_item(request=request, item=parsed_item, ModelSerializer=ModelSerializeer)
    elif request.method == 'PATCH':
        return partial_update_item(request=request, item=parsed_item, ModelSerializer=ModelSerializeer)
    elif request.method == 'DELETE':
        return destroy_item(item=parsed_item)
    else:
        return Response({"detail": "Invalid method for this endpoint."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# Category views
@api_view(['GET', 'POST'])
def categories(request):
    return handle_items(request=request, Model=Category, ModelSerializeer=CategorySerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def single_category(request, item_id=None):
    return handle_item(request=request, item_id=item_id, Model=Category, ModelSerializeer=CategorySerializer)


# MenuItem views
@api_view(['GET', 'POST'])
def menu_items(request):
    return handle_items(request=request, Model=MenuItem, ModelSerializeer=MenuItemSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def single_menu_item(request, item_id=None):
    return handle_item(request=request, item_id=item_id, Model=MenuItem, ModelSerializeer=MenuItemSerializer)


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

class IsGroupOnlyDeliveryCrew(BasePermission):
    """
    Allows access only to Authenticated users with Delivery Crew Group/Role Permissions.
    """
    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and request.user.groups.filter(name=settings.DELIVERY_CREW_GROUP_NAME).exists()


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
            {"status_code": status.HTTP_201_CREATED, "detail": f"{user.username}, Was Successfully Added to {group_name} group."}, 
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
            {"status_code": status.HTTP_200_OK, "detail": f"{user.username}, Was Successfully Deleted from {group_name} group."}, 
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
            {"status_code": status.HTTP_400_BAD_REQUEST, "detail": {"error_message": str(e).replace("'", ""), "username": "This field is required."}}, 
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


def handle_users_group_management(request: HttpRequest, group_name: settings) -> Response:
    """Handle views for a user management actions for a group. Method: GET, POST, DELETE"""
    if request.method == 'GET':
        return get_users_in_group(group_name=group_name)
    elif request.method == 'POST':
        return assign_or_remove_user_from_group(request=request, group_name=group_name, action='assign')
    elif request.method == 'DELETE':
        return assign_or_remove_user_from_group(request=request, group_name=group_name, action='remove')
    else:
        return Response({"detail": "Invalid method for this endpoint."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def handle_user_group_management(request: HttpRequest, user_id: int, group_name: settings) -> Response:
    """Handle views for a user management actions for a single user in a group. Method: DELETE"""
    if request.method == 'DELETE':
        return remove_user_from_group(user_id=user_id, group_name=group_name)
    else:
        return Response({"detail": "Invalid method for this endpoint."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# TODO: refactor naming convension for functions, variable
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsGroupManager])
def manage_manager_users(request):
    return handle_users_group_management(request=request, group_name=settings.MANAGER_GROUP_NAME)

@api_view(['DELETE'])
@permission_classes([IsGroupManager])
def manage_manager_user(request, user_id):
    return handle_user_group_management(request=request, user_id=user_id, group_name=settings.MANAGER_GROUP_NAME)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsGroupManager])
def manage_delivery_crew_users(request):
    return handle_users_group_management(request=request, group_name=settings.DELIVERY_CREW_GROUP_NAME)

@api_view(['DELETE'])
@permission_classes([IsGroupManager])
def manage_delivery_crew_user(request, user_id):
    return handle_user_group_management(request=request, user_id=user_id, group_name=settings.DELIVERY_CREW_GROUP_NAME)


# Cart management

# Custom class Permission for Authenticated users that by default Customer
class IsOnlyCustomer(BasePermission):
    """Only allow access to customers (authenticated users who are not staff within any group like Manager or Delivery crew)"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and not any((
            request.user.is_staff, 
            request.user.groups.filter(name=settings.MANAGER_GROUP_NAME).exists(),
            request.user.groups.filter(name=settings.DELIVERY_CREW_GROUP_NAME).exists()
        ))


# Helper Function for Cart management
def get_user_cart_items(request: HttpRequest) -> Response:
    """Get a list of cart items for the authenticated user."""
    cart_items = Cart.objects.filter(user=request.user)
    
    if not cart_items.exists():
        return Response(
            {"detail": "Your cart is empty. Please add something tasty."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = CartSerializer(cart_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

def add_menu_item_to_cart(request: HttpRequest) -> Response:
    """Add a menu item to the user's cart."""
    menu_item_id = request.data.get('menuitem')
    quantity = request.data.get('quantity')

    # Convert quantity to a numeric type (e.g., int or Decimal)
    try:
        quantity = Decimal(quantity)
    except InvalidOperation as e:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "error_message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Calculate total price
    menu_item = get_object_or_404(MenuItem, id=menu_item_id)
    total_price = menu_item.price * quantity
    
    # Serialize data
    serializer = CartSerializer(data={
        "user": request.user.id,
        "menuitem": menu_item_id,
        "quantity": quantity,
        "unit_price": total_price / quantity,
        "price": total_price
    })
    
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "error_message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


def clean_user_cart_item(request: HttpRequest) -> Response:
    """Delete all cart items added by the authenticated user."""
    Cart.objects.filter(user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def handle_cart_request(request: HttpRequest) -> Response:
    """Handle cart view based on the HTTP method."""
    if request.method == 'GET':
        return get_user_cart_items(request=request)
    elif request.method == 'POST':
        return add_menu_item_to_cart(request=request)
    elif request.method == 'DELETE':
        return clean_user_cart_item(request=request)
    else:
        return Response({"detail": "Invalid method for this endpoint."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsOnlyCustomer])
def cart_items(request):
    return handle_cart_request(request=request)


# Order management
@api_view(['GET', 'POST'])
def orders(request: HttpRequest):
    manager = request.user.groups.filter(name='Manager').exists()
    delivery = request.user.groups.filter(name='Delivery crew').exists()
    admin = request.user.is_staff
    
    if request.method == 'GET':

        if manager or admin:
            # Manager can retrieve all Orders of all users
            orders = Order.objects.all()
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        
        elif delivery:
            orders = Order.objects.filter(delivery_crew=request.user)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        
        else:  # Customer
            # Customer can view created Orders
            orders = Order.objects.filter(user=request.user)
            
            if not orders.exists():
                return Response(
                    {"detail": "Your order is empty. Please add push your cart something tasty and order it."},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
    if request.method == 'POST':
        if manager or admin or delivery:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        else:
            # Current Customer creates new order item, by gets user customer cart items and adds those items to order items table, then it deleted
            cart_items = Cart.objects.filter(user=request.user)

            if not cart_items.exists():
                return Response(
                    {"detail": "Your cart is empty. Please add your cart something tasty."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate total price
            total_price = sum(item.price for item in cart_items)
            
            # Order model Instance
            order = Order.objects.create(
                user=request.user,
                date=datetime.date.today(),
                total=total_price,
                status=False
            )
            
            # OrderItem model Instance
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    menuitem=cart_item.menuitem,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    price=cart_item.price
                )
            
            
            cart_items.delete()
            
            return Response({"message": "Order created successfully"}, status=status.HTTP_201_CREATED)
    
    

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def order(request, order_id):
    manager: bool = request.user.groups.filter(name='Manager').exists()
    delivery: bool = request.user.groups.filter(name='Delivery crew').exists()
    admin: bool = request.user.is_staff
    
    if request.method == 'GET':
        if manager or admin or delivery:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        else:  # Customer
            # Customer can check order items using created order id
            order = get_object_or_404(Order, id=order_id)

            if order.user != request.user:
                return Response(
                    {"error": "Permission denied. This order does not belong to the current user."}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            order_items = OrderItem.objects.filter(order=order)
            
            if not order_items.exists():
                return Response(
                    {"detail": "Your Order is empty. Please add your cart something tasty and order it."},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            serializer = OrderItemSerializer(order_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
       
    if request.method == 'PUT':
        # Manager put specific Delivery by username to deliver this specific order by id of order
        if manager or admin:
            try:
                # TODO: also make it using delivery_id
                parsed_username = request.data['username']
                if not parsed_username:
                    raise KeyError("Delivery crew username is required.")
                
                user = get_object_or_404(User, username=parsed_username)
                if not user.groups.filter(name='Delivery crew').exists():
                    raise ValueError("The specified user is not a part of the 'Delivery crew' group.")
            
            except KeyError as e:
                return Response(
                    {"status_code": status.HTTP_400_BAD_REQUEST, "detail": {"error_message": str(e).replace("'", ""), "username": "Delivery crew username is required."}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except ValueError as e:
                return Response(
                    {"status_code": status.HTTP_400_BAD_REQUEST, "detail": {"error_message": str(e)}},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            order = get_object_or_404(Order, id=order_id)
            order.delivery_crew = user
            order.save()
            
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        
    if request.method == 'PATCH':
        # Manager update status: bool = 0/1, 0(in procces deliver) to 1(delivered) 
        if manager or admin or delivery:
            try:
                #parsed_status = request.data['status']
                parsed_status = request.data.get('status', None)
                #if not parsed_status is None:
                if parsed_status is None:
                    raise KeyError("To change it status field is required.")
                #if not isinstance(parsed_status, bool):
                #    raise TypeError("Status must be 0(false) or 1(true)")
                
                # Convert parsed_status to a boolean
                if parsed_status.lower() == 'true':
                    parsed_status = True
                elif parsed_status.lower() == 'false':
                    parsed_status = False
                else:
                    raise ValueError("Status must be 'true' or 'false'.")

                if not isinstance(parsed_status, bool):
                    raise TypeError("Status must be a boolean (True or False).")
                
            except KeyError as e:
                return Response(
                    {
                        "status_code": status.HTTP_400_BAD_REQUEST, 
                        "detail": {"error_message": {str(e).replace("'", "")}},
                        "raised_message": "To change it status field is required."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            #except TypeError as e:
            except (TypeError, ValueError) as e:
                return Response(
                    {"status_code": status.HTTP_400_BAD_REQUEST, "detail": {"error_message": str(e)}},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            order = get_object_or_404(Order, id=order_id)
            order.status = parsed_status
            order.save()
            
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)


    if request.method == 'DELETE':
        # Only Manager and Admin can delete order and orderitem using order_id
        if manager or admin:
            order = get_object_or_404(Order, id=order_id)
            order_items = OrderItem.objects.filter(order=order)
            order.delete()
            order_items.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Permission denied."})



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