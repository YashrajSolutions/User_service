from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import user_details
from .serializer import serializer_user,user_serailizer_by_id
import time 
from functools import wraps
from rest_framework.decorators import api_view

def measure_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time:.4f} seconds")
        return result
    return wrapper


@csrf_exempt
@measure_execution_time
def create_user(request):
    try:
        if request.method == "POST":   #checking format of data
            if type(request) != dict:
                request_data = json.loads(request.body)
            else:
                request_data = request
            
            serializer = serializer_user(data=request_data) 
            if serializer.is_valid():   
                serializer.save()
               
                return JsonResponse({"message":"User created successfully!!","data":serializer.data},status=201)
            else:
                print("serializer---->",serializer)
                return JsonResponse({"message":"Invalid Data Provided"})
        else:
            return JsonResponse({"message": "Invalid Http Method"},status=405)
    except Exception as error:
        return JsonResponse({"message":"Something went wrong","error":str(error)},status=500)
    
@csrf_exempt
@measure_execution_time
def read_user(request,pk):
    try:
        user = user_details.objects.get(pk=pk, is_deleted=False)
        serializer = serializer_user(user)
        return JsonResponse({"message":"User details retrieved successfully!!","data":serializer.data})
    except Exception as error:
        return JsonResponse({"message":"Something went wrong","error":str(error)},status=500)
    
@csrf_exempt
@measure_execution_time
def get_all_user_list(request):
    try:
        user_object = user_details.objects.filter(is_deleted=False)
        serializer = serializer_user(user_object, many=True)
        if serializer.data:
            return JsonResponse({"message":"User details retrieved successfully!!","total":len(serializer.data),"data":serializer.data})
        else:
            return JsonResponse({"message":"No data found!!"})
    except Exception as error:
        print("get_all_user_list(): ", error)
        return JsonResponse({"message":"Something went wrong"},status=500)

@csrf_exempt
@measure_execution_time
def update_user(request, pk):
    try:
        user = user_details.objects.get(pk=pk)
        if request.method == 'PUT':
            if type(request) != dict:
                request_data = json.loads(request.body)
            serializer = serializer_user(user, data=request_data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({"message": "User updated successfully!!!", "data": serializer.data})
            else:
                return JsonResponse({"message": "Invalid data provided", "errors": serializer.errors}, status=400)
        else:
            return JsonResponse({"message": "Invalid HTTP method"}, status=405)
    except Exception as error:
        return JsonResponse({"message": "Something went wrong", "error": str(error)}, status=500)


@csrf_exempt
@measure_execution_time
def delete_user(request, pk):
    try:
        user = user_details.objects.get(pk=pk)
        if request.method == 'DELETE':
            user.delete()
            return JsonResponse({"message": "User deleted successfully!!!"})
        else:
            return JsonResponse({"message": "Invalid HTTP method"}, status=405)
    except Exception as error:
        return JsonResponse({"message": "Something went wrong", "error": str(error)}, status=500)



# Inter-Service Call for vehicle onboarding on date given

import requests


def get_vehicle_details_by_date(date):
    try:
        response = requests.get('http://vehicle-service-url/api/vehicle-service/details-by-date', params={'date': date})
        if response.status_code == 200:
            data = response.json()
            return data['data']
        
        else:
            return JsonResponse({"message": "Failed to fetch vehicle details"}, status=500)
    except Exception as error:
        print("Error:", error)
        return None
    
    

# Interservice Call for getting vehicle details from user_id

@api_view(['GET'])   
@csrf_exempt
def get_user_details_by_id_with_all_vehicles(request):
    try:
        user_id = request.GET.get('user_id')  
        if user_id:
            print(user_id)
            user_object = user_details.objects.filter(user_id=user_id, is_deleted=False)
            user = user_details.objects.get(user_id=user_id, is_deleted=False)
            print(user_details)
            # print(user)

            serializer = serializer_user(user)
            print(serializer.data)
            
            if user_object.exists:
                print(user_id)
                # INterservice call to get vehicle data for user_id..
                vehicle_response = requests.get("http://localhost:6000/api/vehicle-service/details-by-id",params={'user_id':user_id})
                print(vehicle_response)
                if vehicle_response.status_code==200:
                    vehicle_data=vehicle_response.json().get('data',())
                else:
                    print(vehicle_response)
                    vehicle_data=[]    

                data = {
                    "user_details":serializer.data,
                    "vehicle_details":vehicle_data
                }
                return JsonResponse({"message": f"User details for {user_id} retrieved successfully!!", "data": data})
            else:
                return JsonResponse({"message": f"No vehicle details found for {user_id}"})
        else:
            return JsonResponse({"message": "Date parameter is missing."}, status=400)
    except Exception as error:
        return JsonResponse({"message": "Something went wrong", "error": str(error)}, status=500)
