from rest_framework import serializers
from .models import *


    
        
        


    
    
class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['student'] = instance.student.f_name  
        data['student'] = instance.student.l_name  
        return data
class StudentsSerializer(serializers.ModelSerializer):
    student = AttendanceSerializer(many=True, read_only=True)

    class Meta:
        model = Students
        fields = ['f_name','l_name','email','phone','username','group','student']


class GroupSerializer(serializers.ModelSerializer):
    group = StudentsSerializer(many=True, read_only=True)
    class Meta:

        model = Group
        fields = ['name','date','group']

    
    