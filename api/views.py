from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404


from .models import Category, MenuItem
from api.serializers import CategorySerializer, MenuItemSerializer


# Function based views
# Category views
@api_view(['GET', 'POST'])
def categories(request):
    if request.method == 'GET':
        items = Category.objects.all()
        serializer = CategorySerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        manager = request.user.groups.filter(name='Manager').exists()
        admin = request.user.is_staff
        if manager or admin:
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"status_code": 403, "message": "Unauthorized - Permission Denied."},
                status=status.HTTP_403_FORBIDDEN
            )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def single_category(request, item_id=None):
    try:
        item = get_object_or_404(Category, pk=item_id)
    except Category.DoesNotExist:
        return Response(
            {"status_code": 404, "message": "Resource Not Found or Does Not Exist."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = CategorySerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    manager = request.user.groups.filter(name='Manager').exists()
    admin = request.user.is_staff
    if manager or admin:
        if request.method == 'PUT':
            serializer = CategorySerializer(item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'PATCH':
            serializer = CategorySerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'DELETE':
            item.delete()
            return Response(
                {"status_code": 204, "message": "Item Successfully deleted."},
                status=status.HTTP_204_NO_CONTENT
            )
    else:
        return Response(
            {"status_code": 403, "message": "Unauthorized - Permission Denied."},
            status=status.HTTP_403_FORBIDDEN
        )

# Menu-Item views
@api_view(['GET', 'POST'])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        manager = request.user.groups.filter(name='Manager').exists()
        admin = request.user.is_staff
        if manager or admin:
            serializer = MenuItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"status_code": 403, "message": "Unauthorized - Permission Denied."},
                status=status.HTTP_403_FORBIDDEN
            )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def single_menu_item(request, item_id=None):
    try:
        item = get_object_or_404(MenuItem, pk=item_id)
    except MenuItem.DoesNotExist:
        return Response(
            {"status_code": 404, "message": "Resource Not Found or Does Not Exist."},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = MenuItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    manager = request.user.groups.filter(name='Manager').exists()
    admin = request.user.is_staff
    if manager or admin:
        if request.method == 'PUT':
            serializer = MenuItemSerializer(item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'PATCH':
            serializer = MenuItemSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        elif request.method == 'DELETE':
            item.delete()
            return Response(
                {"status_code": 204, "message": "Item Successfully deleted."},
                status=status.HTTP_204_NO_CONTENT
            )
    else:
        return Response(
            {"status_code": 403, "message": "Unauthorized - Permission Denied."},
            status=status.HTTP_403_FORBIDDEN
        )


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
