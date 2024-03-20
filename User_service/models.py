from django.db import models
import json

class user_details(models.Model):
    user_id = models.CharField(max_length=16, primary_key=True) #change
    user_fname = models.CharField(max_length=15)
    user_mname = models.CharField(max_length=15, null=True)
    user_lname = models.CharField(max_length=15,null=True)
    pan_number = models.CharField(max_length=10, unique=True)
    email_id = models.EmailField(max_length=20, unique=True)
    #keycloak_id = models.CharField(max_length=50, unique=True) #change
    #profile_img = models.URLField(max_length=200)
    phone_number = models.IntegerField(unique=True)
    address = models.CharField(max_length=100,null=True)
    dob = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __meta__():
        table_name = "user_details"

    def delete(self, *args, **kwargs): 
        self.is_deleted = True
        self.save()   

    # def get(self, id):
    #     return json.loads(self.objects.filter(is_deleted = False, user_id=id))