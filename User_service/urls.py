"""
URL configuration for User_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import path
from . import views

urlpatterns = [
    path('api/user_service/create-user', views.create_user, name='create_user'),
    path('api/user_service/<str:pk>/update-existing-user', views.update_user, name='update_user'),
    path('api/user-service/pk=<str:pk>', views.read_user, name='read_user'),
    path('api/user-service', views.get_all_user_list, name='get_all_user_list'),   
    path('api/user-service/<str:pk>/delete-user', views.delete_user, name='delete_user'),
    path('api/user-service/get-user-details-by-id-with-all-vehicles', views.get_user_details_by_id_with_all_vehicles, name='get_user_details_by_id_with_all_vehicles'),
    

]