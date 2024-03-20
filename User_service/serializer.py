from rest_framework import serializers
from .models import user_details
 
class serializer_user(serializers.ModelSerializer):
    class Meta :
        many = True
        model = user_details
        fields = '__all__'

class user_serailizer_by_id(serializers.ModelSerializer):
    class Meta :
        model = user_details
        fields = '__all__'