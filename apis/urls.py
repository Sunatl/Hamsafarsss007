from django.urls import path
from .views import *

urlpatterns = [
    path("student/",StudentsListCreateView.as_view(),name="student"),
    path("student/<int:pk>/",StudentsRetrieveUpdateDestroyView.as_view(),name="student"),
    path("gruop/",GroupListCreateView.as_view(),name="group"),
    path("gruop/<int:pk>/",GroupRetrieveUpdateDestroyView.as_view(),name="gruop"),
    path("atten/",AttendanceListCreateView.as_view(),name="atten"),
    path("atten/<int:pk>/",AttendanceRetrieveUpdateDestroyView.as_view(),name="atten"),
    path("black/",BlackListAPIView.as_view(),name="Black"),
    path("white/",WhiteListAPIView.as_view(),name="White"),
]
