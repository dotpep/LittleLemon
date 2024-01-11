from django.urls import path, include
from . import views

urlpatterns = [
    path('manager-view/', views.manager_view),
]