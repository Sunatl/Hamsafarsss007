from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView,ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import *
from .serialayzer import *
from django.utils import timezone
from datetime import timedelta




class StudentsListCreateView(ListCreateAPIView):
    queryset = Students.objects.all()
    serializer_class = StudentsSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['f_name', 'phone', 'username']
    search_fields = ['f_name', 'phone','username']
    ordering_fields = ['f_name', 'phone','username']
    


class StudentsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Students.objects.all()
    serializer_class = StudentsSerializer
    
class GroupListCreateView(ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['name']
    search_fields = ['name']
    ordering_fields = ['name']


    

class GroupRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class AttendanceListCreateView(ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['student']
    search_fields = ['student__f_name']
    ordering_fields = ['student']


class AttendanceRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    


class BlackListAPIView(ListAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        group_id = self.request.query_params.get('group', None)

        if group_id:
            group = Group.objects.get(id=group_id)
            group_start_time = group.date

            queryset = queryset.filter(omadan__gt=group_start_time)  

        return queryset


class WhiteListAPIView(ListAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        group_id = self.request.query_params.get('group', None)

        if group_id:
            group = Group.objects.get(id=group_id)
            group_start_time = group.date  

            queryset = queryset.filter(omadan__lte=group_start_time)

        return queryset