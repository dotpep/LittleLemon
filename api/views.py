from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view()
def manager_view(request):
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
