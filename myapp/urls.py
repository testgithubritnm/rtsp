from django.urls import path
from .views import CameraListAPIView,CameraDetailAPIView,CameraUpdateAPIView,CameraDeleteAPIView
from . import views
from .views import live_stream
from django.urls import path





urlpatterns = [
    
    path('create/', CameraListAPIView.as_view(),name='camera-create'),
    path('camera/get/', CameraDetailAPIView.as_view(), name='camera-detail'),
    path('camera/update/', CameraUpdateAPIView.as_view(),name='camera-update'),
    path('camera/delete/', CameraDeleteAPIView.as_view(),name='camera-delete'),
    path('live-stream/', live_stream, name='live_stream'),
    path('discover-devices/', views.discover_devices, name='discover_devices'),
    


]

    
    
    
     
    
    

    

    



    
    

