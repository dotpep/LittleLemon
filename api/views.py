from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import datetime


from api.models import Category, MenuItem, Cart, Order, OrderItem
from api.serializers import CategorySerializer, MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from django.contrib.auth.models import User, Group

from django.conf import settings


# Validation
from django.forms import ValidationError
from decimal import Decimal, InvalidOperation

# Filtering
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

# Pagination
from django.core.paginator import Paginator, EmptyPage

# for Custom class Permission
from rest_framework.permissions import BasePermission

# Type hinting
from django.contrib.auth.models import User
from django.db.models import Model
from rest_framework.serializers import ModelSerializer
from django.http import HttpRequest
from typing import Literal


# TODO: apply Clean architecture, separate each services, helper functions and etc.

# Helper Function for Category and MenuItem views
def is_group_has_permission(request: HttpRequest, group_name: str) -> bool:
    """Check if user is in the specified group or is a staff member."""
    user = request.user
    return any((user.groups.filter(name=group_name).exists(), user.is_staff))


def get_list_of_item(items: Model, serializer_class: ModelSerializer) -> Response:
    """Get a list of items. Method: GET"""
    serializer = serializer_class(items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

def create_new_item(request: HttpRequest, serializer_class: ModelSerializer) -> Response:
    """Create a new item. Method: POST"""
    serializer = serializer_class(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "error_message": str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

def retrieve_item(item: Model, serializer_class: ModelSerializer) -> Response:
    """Retrieve details for a single item. Method: GET"""
    # FIXME: name convention for Model and ModelSerializer in func params
    serializer = serializer_class(item)
    return Response(serializer.data, status=status.HTTP_200_OK)

def update_full_item(request: HttpRequest, item: Model, serializer_class: ModelSerializer) -> Response:
    """Update an existing item. Method: PUT"""
    serializer = serializer_class(item, data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    except ValidationError as e:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "error_message": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

def partial_update_item(request: HttpRequest, item: Model, serializer_class: ModelSerializer) -> Response:
    """Partially update an existing item. Method: PATCH"""
    serializer = serializer_class(item, data=request.data, partial=True)
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

# Helper function for Pagination

# Helper function for Filtering, Searching, Ordering/Sorting

def filter_by_category(items, category_slug):
    return items.filter(category__slug__iexact=category_slug)

def filter_by_price(items, to_price):
    return items.filter(price__lte=Decimal(to_price))

def filter_by_featured(items, featured):
    featured = bool(int(featured))
    return items.filter(featured=featured)

def search_by_title(items, search):
    return items.filter(title__icontains=search)

def order_items(items, order_by):
    return items.order_by(*order_by)


def filter_by_param(request, items, param_name, filter_func):
    param_value = request.query_params.get(param_name)
    if param_value:
        items = filter_func(items, param_value)
    return items


def handle_menuitem_filtering(request: HttpRequest, items):
    items = filter_by_param(request=request, items=items, param_name='category', filter_func=filter_by_category)
    items = filter_by_param(request=request, items=items, param_name='to_price', filter_func=filter_by_price)
    items = filter_by_param(request=request, items=items, param_name='featured', filter_func=filter_by_featured)
    
    items = filter_by_param(request=request, items=items, param_name='search', filter_func=search_by_title)
    
    return items


def handle_category_filtering(request: HttpRequest, items):
    items = filter_by_param(request=request, items=items, param_name='search', filter_func=search_by_title)
    
    return items


def handle_items(request: HttpRequest, model_class: Model, serializer_class: ModelSerializer) -> Response:
    """Handle views for a list of items and create new item. Method: GET, POST"""
    if request.method == 'GET':
        #items = model_class.objects.all()
        
        if model_class is MenuItem:
            items = model_class.objects.select_related('category').all()
            items = handle_menuitem_filtering(request=request, items=items)
            #items = items.order_by('title', 'price')
        
        if model_class is Category:
            items = model_class.objects.all()
            items = handle_category_filtering(request=request, items=items)
            #items = items.order_by('title', 'id')
        
        ## Ordering
        #ordering = request.query_params.get('ordering')
        #if ordering:
        #    ordering_fields = ordering.split(",")  # for many fields or values passed into ?ordering query parameters
        #    items = items.order_by(*ordering_fields)
        
        ## Pagination
        #perpage = request.query_params.get('perpage', default=2)
        #page = request.query_params.get('page', default=1)
        
        #paginator = Paginator(items, per_page=perpage)
        #try:
        #    items = paginator.page(number=page)
        #except EmptyPage:
        #    items = []
        
        return get_list_of_item(items=items, serializer_class=serializer_class)
    
    # Check Permissions for POST
    if not is_group_has_permission(request=request, group_name=settings.MANAGER_GROUP_NAME):
        return Response(
            {"status_code": status.HTTP_403_FORBIDDEN, "error_message": "Permission Denied."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    if request.method == 'POST':
        return create_new_item(request=request, serializer_class=serializer_class)
    else:
        return Response({"detail": "Invalid method for this endpoint."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def handle_item(request: HttpRequest, item_id: int, model_class: Model, serializer_class: ModelSerializer) -> Response:
    """Handle views for a single item and manipulate item. Method: GET, PUT, PATCH, DELETE"""
    try:
        parsed_item = get_object_or_404(model_class, pk=item_id)
    except model_class.DoesNotExist as e:
        return Response(
            {"status_code": status.HTTP_404_NOT_FOUND, "error_message": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        return retrieve_item(item=parsed_item, serializer_class=serializer_class)
    
    # Check Permissions for PUT, PATCH, DELETE
    if not is_group_has_permission(request=request, group_name=settings.MANAGER_GROUP_NAME):
            return Response(
                {"status_code": status.HTTP_403_FORBIDDEN, "error_message": "Permission Denied."},
                status=status.HTTP_403_FORBIDDEN
            )
    
    if request.method == 'PUT':
        return update_full_item(request=request, item=parsed_item, serializer_class=serializer_class)
    elif request.method == 'PATCH':
        return partial_update_item(request=request, item=parsed_item, serializer_class=serializer_class)
    elif request.method == 'DELETE':
        return destroy_item(item=parsed_item)
    else:
        return Response({"detail": "Invalid method for this endpoint."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# Category views
@api_view(['GET', 'POST'])
def categories(request: HttpRequest):
    return handle_items(request=request, model_class=Category, serializer_class=CategorySerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def single_category(request: HttpRequest, item_id: int=None):
    return handle_item(request=request, item_id=item_id, model_class=Category, serializer_class=CategorySerializer)


# MenuItem views
@api_view(['GET', 'POST'])
def menu_items(request: HttpRequest):
    return handle_items(request=request, model_class=MenuItem, serializer_class=MenuItemSerializer)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def single_menu_item(request: HttpRequest, item_id: int=None):
    return handle_item(request=request, item_id=item_id, model_class=MenuItem, serializer_class=MenuItemSerializer)


# User group management

# Custom class Permission for Manager and Delivery Crew groups
class IsGroupManager(BasePermission):
    """
    Allows access only to Authenticated users with Manager Group/Role Permissions.
    """
    @staticmethod
    def has_permission(request, view) -> bool:
        user = request.user
        return user.is_authenticated and any((
            user.is_staff, 
            user.groups.filter(name=settings.MANAGER_GROUP_NAME).exists()
        ))

class IsGroupOnlyDeliveryCrew(BasePermission):
    """
    Allows access only to Authenticated users with Delivery Crew Group/Role Permissions.
    """
    @staticmethod
    def has_permission(request, view) -> bool:
        user = request.user
        return user.is_authenticated and user.groups.filter(name=settings.DELIVERY_CREW_GROUP_NAME).exists()


# Helper Function for User group management
def get_users_in_group(group_name: str) -> Response:
    """Get a list of users belonging to the specified group. Method: GET"""
    users = User.objects.filter(groups__name=group_name)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

def assign_user_to_group(user: User, group_name: str) -> Response:
    """Assign the given user to the specified group. Method: POST"""
    group = Group.objects.get(name=group_name)
    
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

def remove_user_from_group(user_id: int, group_name: str) -> Response:
    """Remove the specified user from the specified group using the user's ID. Method: DELETE"""
    user = get_object_or_404(User, id=user_id)
    group = Group.objects.get(name=group_name)
    
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

def assign_or_remove_user_from_group(
    request: HttpRequest, group_name: str, 
    action: Literal["assign", "remove"]) -> Response:
    """Assign or remove a user from the specified group based on the action parameter. Action: assign for POST, remove for DELETE"""
    try:
        username: str = request.data['username']
        user: User = get_object_or_404(User, username=username)
        user_id: int = user.id
    except KeyError as e:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "detail": {"error_message": str(e).replace("'", ""), "username": "This field is required."}}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    if action == 'assign':
        return assign_user_to_group(user=user, group_name=group_name)
    elif action == 'remove':
        return remove_user_from_group(user_id=user_id, group_name=group_name)
    else:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "error_message": "Invalid action."},
            status=status.HTTP_400_BAD_REQUEST
        )


def handle_users_group_management(request: HttpRequest, group_name: str) -> Response:
    """Handle views for a user management actions for a group. Method: GET, POST, DELETE"""
    if request.method == 'GET':
        return get_users_in_group(group_name=group_name)
    elif request.method == 'POST':
        return assign_or_remove_user_from_group(request=request, group_name=group_name, action='assign')
    elif request.method == 'DELETE':
        return assign_or_remove_user_from_group(request=request, group_name=group_name, action='remove')
    else:
        return Response({"detail": "Invalid method for this endpoint."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


def handle_user_group_management(request: HttpRequest, user_id: int, group_name: str) -> Response:
    """Handle views for a user management actions for a single user in a group. Method: DELETE"""
    if request.method == 'DELETE':
        return remove_user_from_group(user_id=user_id, group_name=group_name)
    else:
        return Response({"detail": "Invalid method for this endpoint."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsGroupManager])
def manage_manager_users(request: HttpRequest):
    return handle_users_group_management(request=request, group_name=settings.MANAGER_GROUP_NAME)

@api_view(['DELETE'])
@permission_classes([IsGroupManager])
def manage_manager_user(request: HttpRequest, user_id: int):
    return handle_user_group_management(request=request, user_id=user_id, group_name=settings.MANAGER_GROUP_NAME)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsGroupManager])
def manage_delivery_crew_users(request: HttpRequest):
    return handle_users_group_management(request=request, group_name=settings.DELIVERY_CREW_GROUP_NAME)

@api_view(['DELETE'])
@permission_classes([IsGroupManager])
def manage_delivery_crew_user(request: HttpRequest, user_id: int):
    return handle_user_group_management(request=request, user_id=user_id, group_name=settings.DELIVERY_CREW_GROUP_NAME)


# Cart management

# Custom class Permission for Authenticated users that by default Customer
class IsOnlyCustomer(BasePermission):
    """Only allow access to customers (authenticated users who are not staff within any group like Manager or Delivery crew)"""
    @staticmethod
    def has_permission(request, view):
        user = request.user
        return user.is_authenticated and not any((
            user.is_staff, 
            user.groups.filter(name=settings.MANAGER_GROUP_NAME).exists(),
            user.groups.filter(name=settings.DELIVERY_CREW_GROUP_NAME).exists()
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
    #try:
    #    menu_item_id = request.data['menuitem']
    #    quantity = request.data['quantity']

    #    if not menu_item_id:
    #        raise KeyError("menuitem", "Menu item ID is required.")

    #    if not quantity:
    #        raise KeyError("quantity", "Quantity is required.")
    #    else:
    #        try:
    #            quantity = Decimal(quantity)
    #        except InvalidOperation:
    #            raise ValueError("quantity", "Enter a valid number for quantity.")

    #except KeyError as e:
    #    error_detail = {str(e): "This field is required."}
    #    return Response(
    #        {"status_code": status.HTTP_400_BAD_REQUEST, "detail": error_detail},
    #        status=status.HTTP_400_BAD_REQUEST
    #    )
    #except ValueError as e:
    #    field, message = e.args
    #    error_detail = {field: message}
    #    return Response(
    #        {"status_code": status.HTTP_400_BAD_REQUEST, "detail": error_detail},
    #        status=status.HTTP_400_BAD_REQUEST
    #    )
    
    
    menu_item_id = request.data.get('menuitem')
    quantity = request.data.get('quantity')

    error_messages = {}

    if menu_item_id is None:
        error_messages['menuitem'] = 'This field is required.'

    if quantity is None:
        error_messages['quantity'] = 'This field is required.'
    else:
        try:
            quantity = Decimal(quantity)
        except InvalidOperation:
            error_messages['quantity'] = 'Enter a valid number.'

    if error_messages:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "detail": error_messages},
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
def get_user_role(request: HttpRequest) -> str:
    is_manager_or_admin = IsGroupManager.has_permission(request=request, view=None)
    is_delivery_crew = IsGroupOnlyDeliveryCrew.has_permission(request=request, view=None)
    
    if is_manager_or_admin:
        return 'manager'
    elif is_delivery_crew:
        return 'delivery'
    else:  # Customer
        return 'customer'

def permission_denied(request: HttpRequest=None, order_id: int=None) -> Response:
    return Response(
        {"detail": "Permission Denied."},
        status=status.HTTP_403_FORBIDDEN
    )

def process_request(request: HttpRequest, method_handlers: dict):
    """Dispatcher function to select the handler based on the user's role and HTTP method."""
    user_group_router = get_user_role(request=request)
    
    # Get the specific handlers for the current HTTP method
    request_handler = method_handlers[request.method]
    
    # Find the appropriate handler for the user's role
    # If not found, default to the permission_denied handler
    method_handler = request_handler.get(user_group_router, permission_denied())
    
    # Get the method that will be used to pass an argument to our functions in the dictionary
    return method_handler


def get_all_orders(request: HttpRequest=None) -> Response:
    """Manager can retrieve all Orders of all users"""
    orders = Order.objects.select_related('user').all()
    
    orders = handle_order_filtering(request=request, items=orders)
    #orders = orders.order_by('date', 'unit_price')
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

def get_delivery_orders(request: HttpRequest) -> Response:
    orders = Order.objects.filter(delivery_crew=request.user)
    
    if not orders.exists():
        return Response(
            {"detail": "You currently have an Empty Delivery Request."},
            status=status.HTTP_200_OK
        )
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

def get_user_orders(request: HttpRequest) -> Response:
    """Customer can view created Orders"""
    orders = Order.objects.filter(user=request.user)
    
    if not orders.exists():
        return Response(
            {"detail": "Your order is empty. Please add push your cart something tasty and order it."},
            status=status.HTTP_200_OK
        )

    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def create_new_order(request: HttpRequest) -> Response:
    """Current Customer creates new order item, by gets user customer cart items and adds those items to order items table, then it deleted"""
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return Response(
            {"detail": "Your cart is empty. Please add your cart something tasty."},
            status=status.HTTP_200_OK
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


def get_user_order_items(request: HttpRequest, order_id: int) -> Response:
    """Customer can check order items using created order id"""
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
            status=status.HTTP_200_OK
        )
        
    serializer = OrderItemSerializer(order_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def set_delivery_to_order(request: HttpRequest, order_id: int) -> Response:
    """Manager put specific Delivery by username to deliver this specific order by id of order"""
    try:
        username = request.data['username']
        if not username:
            raise KeyError("Delivery crew username is required.")
        
        user = get_object_or_404(User, username=username)
        if not user.groups.filter(name='Delivery crew').exists():
            raise ValueError("The specified user is not a part of the 'Delivery crew' group.")
    
    except KeyError as e:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "detail": {"error_message": str(e).replace("'", ""), "username": "This Delivery crew field is required."}},
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


def update_order_status(request: HttpRequest, order_id: int) -> Response:
    """Manager or Delivery updates order status 0 - in procces or 1 - delivered"""
    order = get_object_or_404(Order, id=order_id)
    
    #manager = is_group_has_permission(request=request, group_name=settings.MANAGER_GROUP_NAME)
    #delivery = is_group_has_permission(request=request, group_name=settings.DELIVERY_CREW_GROUP_NAME)
    
    is_manager_or_admin = IsGroupManager.has_permission(request=request, view=None)
    is_delivery_crew = IsGroupOnlyDeliveryCrew.has_permission(request=request, view=None)
    try:
        if is_manager_or_admin or is_delivery_crew:
            status_data = request.data['status']
            
        if not status_data:
            raise KeyError("Status field is required.")
        
        if status_data is not None and status_data in [str(0), str(1)]:
            order.status = status_data
            order.save()

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {'error': 'Invalid status value. It should be 0 (in process) or 1 (delivered).'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except KeyError as e:
        return Response(
            {"status_code": status.HTTP_400_BAD_REQUEST, "detail": {"error_message": str(e).replace("'", ""), "status": "This field is required."}},
            status=status.HTTP_400_BAD_REQUEST
        )


def delete_single_order(order_id: int, request: HttpRequest=None) -> Response:
    """Only Manager and Admin can delete order and orderitem using order_id"""
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    order.delete()
    order_items.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def handle_orders(request: HttpRequest) -> Response:
    method_handlers: dict = {
        'GET': {
            'manager': get_all_orders,
            'delivery': get_delivery_orders,
            'customer': get_user_orders,
        },
        'POST': {
            'manager': permission_denied,
            'delivery': permission_denied,
            'customer': create_new_order,
        }
    }
    
    # Dispatching Using a Dictionary for request.method and has_permissions group/role by executing function with passed arguments
    dict_dispatcher_method = process_request(request=request, method_handlers=method_handlers)
    
    return dict_dispatcher_method(request=request)


def handle_order(request: HttpRequest, order_id: int) -> Response:
    method_handlers: dict = {
        'GET': {
            'manager': permission_denied,
            'delivery': permission_denied,
            'customer': get_user_order_items,
        },
        'PUT': {
            'manager': set_delivery_to_order,
            'delivery': permission_denied,
            'customer': permission_denied,
        },
        'PATCH': {
            'manager': update_order_status,
            'delivery': update_order_status,
            'customer': permission_denied,
        },
        'DELETE': {
            'manager': delete_single_order,
            'delivery': permission_denied,
            'customer': permission_denied,
        }
    }
    
    dict_dispatcher_method = process_request(request=request, method_handlers=method_handlers)
    
    return dict_dispatcher_method(request=request, order_id=order_id)


@api_view(['GET', 'POST'])
def orders(request: HttpRequest):
    return handle_orders(request=request)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def order(request: HttpRequest, order_id: int):
    return handle_order(request=request, order_id=order_id)


# Testing
if __name__ == "__main__":
    # to run `python manage.py shell -i ipython` and in ipython `%run api/request.py`
    from decimal import Decimal
    from django.http import HttpRequest
    from rest_framework.response import Response
    from api.models import MenuItem, Category, Cart
    from api.serializers import MenuItemSerializer
    from django.db.models import Model

    #
    # MenuItem Filtering, Searching, Ordering and Pagination
    #
    class _TestingMenuItemProcessor:
        def __init__(self, request: HttpRequest) -> None:
            self.request = request
            self.items = MenuItem.objects.select_related('category').all()
            
        def _searching(self) -> Model:
            search = self.request.GET.get('search')
            if search:
                self.items = self.items.filter(title__icontains=search)
            return self.items

        def _filter_by_price(self) -> Model:
            to_price = self.request.GET.get('to_price')
            if to_price:
                self.items = self.items.filter(price__lte=Decimal(to_price))

        def _filter_by_category(self) -> Model:
            category_slug = self.request.GET.get('category')
            if category_slug:
                self.items = self.items.filter(category__slug__iexact=category_slug)
            return self.items

        def _ordering(self) -> Model:
            ordering = self.request.GET.get('ordering')
            if ordering:
                ordering_fields = ordering.split(",")
                self.items = self.items.order_by(*ordering_fields)
            return self.items

        def custom_process_menu_items(self) -> Response:
            if self.request.method == 'GET':
                self._searching()
                self._filter_by_price()
                self._filter_by_category()
                self._ordering()

                serialized_item = MenuItemSerializer(items, many=True)
                return Response(serialized_item.data)
    
    #
    # MenuItem manipulation
    #
    items = MenuItem.objects.all()
    
    fields = ['title', 'price', 'featured', 'category']
    
    item_map: dict = {
        'title': items.values_list('title', flat=True),
        'price': items.values_list('price', flat=True),
        'featured': items.values_list('featured', flat=True),
        'category': items.values_list('category__title', flat=True),
    }
    
    item_fields: list = [key for key in item_map.keys()]
    
    #print(item_map['title'])
    
    
    while True:
        item_id = input('menu item id or (q, quit): ')
        if item_id.lower() in ('quit', 'q'):
            break
        
        for field in item_fields:
            try:
                menu_item = item_map[field][int(item_id)]
            except (IndexError, ValueError): continue
            print(f"{field.title()}: {menu_item}")

    
    count = MenuItem.objects.count()
    #print(count)
    
    serialized_item = MenuItemSerializer(items, many=True)
    response = Response(serialized_item.data)
    #print(response.data)
    
    #
    # MenuItem in memory, stack and hash
    #
    hex(id(MenuItem))
    hex(id(MenuItem.objects.all()))
    hex(id(items))

    #
    # MenuItem Request and Response
    #
    query_params = {'search': 'Apple cake'}
    
    request = HttpRequest()
    request.method = 'GET'
    request.GET = query_params

    menu_processor = _TestingMenuItemProcessor(request=request)
    response = menu_processor.custom_process_menu_items()

    #response = _custom_menu_items(request)
    print(response.data)
