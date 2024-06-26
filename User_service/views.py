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
            user_object = user_details.objects.filter(user_id=user_id, is_deleted=False)
            user = user_details.objects.get(user_id=user_id, is_deleted=False)

            serializer = serializer_user(user)
            print(serializer.data)
            
            if user_object.exists:
                print(user_id)
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


# Interservice Call for fetching details from Range of Dates given by User

from datetime import datetime
from django.core.paginator import Paginator

def get_vehicles_details_in_date_range(start_date,end_date,page_number):
    try:

        #parse
        start_date = datetime.strptime(start_date, '%d-%m-%Y')
        end_date = datetime.strptime(end_date, '%d-%m-%Y')

        #format the dates
        start_date_standard = start_date.strftime('%Y-%m-%d')
        end_date_standard = end_date.strftime('%Y-%m-%d')

        #params 
        params = {'start_date': start_date_standard, 'end_date': end_date_standard}

        if params.exists:
            response = requests.get("http://localhost:6000/api/vehicle-service/get_vehicle_details_by_date_range",params=params)

            if response.status_code==200:
                data=response.json
                sorted_data = sorted(data['data'], key=lambda x: x['created_at'])

                paginator = Paginator(sorted_data, 5)  # 5 results per page
                page_obj = paginator.get_page(page_number)
                
                return page_obj.object_list
            else:
                return JsonResponse({"message": "Failed to fetch details"}, status=500)
        else:
            return JsonResponse({'message':'Date Parameter is missing'},status=400)
        
    except Exception as error:
        print("Error",error)
        return None


    
# Interservice call for converting UST to IST and fetching details
    
def get_vehicle_details_for_ust(start_date,end_date):
    
    try:

        start_date_utc = datetime.strptime(start_date, '%d-%m-%Y %H:%M')
        end_date_utc = datetime.strptime(end_date, '%d-%m-%Y %H:%M')

        if start_date_utc.tzinfo != None and end_date_utc.tzinfo != None:
            if start_date_utc.tzinfo.utcoffset(start_date_utc) & end_date_utc.tzinfo.utcoffset(end_date_utc):
                params = {'start_date':start_date_utc, 'end_date':end_date_utc}
                response = requests.get("http://localhost:6000/api/vehicle-service/get_vehicle_details_for_ust",params=params)

                if response.status_code == 200:
                    data=response.json
                    sorted_data = sorted(data['data'], key=lambda x: x['created_at'])
                    return sorted_data
                else:
                    return JsonResponse({"message":"Failed to Fetch Details"})
            else:
                return JsonResponse({"message":"Invalid Date Format"},status=500)
        else:
            return JsonResponse({'message':'Date Parameter is missing'},status=400)


    except Exception as e:
        print("Error",e)
        return None