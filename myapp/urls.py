from django.urls import path
from .views import CameraListAPIView,CameraDetailAPIView,CameraUpdateAPIView,CameraDeleteAPIView
from . import views
from .views import GetRTSPUrlView
from .views import live_stream
from .views import DeviceManagementView





urlpatterns = [
    
    path('create/', CameraListAPIView.as_view(),name='camera-create'),
    path('camera/get/', CameraDetailAPIView.as_view(), name='camera-detail'),
    path('camera/update/', CameraUpdateAPIView.as_view(),name='camera-update'),
    path('camera/delete/', CameraDeleteAPIView.as_view(),name='camera-delete'),
    path('get-rtsp-url/', GetRTSPUrlView.as_view(), name='get_rtsp_url'),
    path('live-stream/', live_stream, name='live_stream'),
    path('device-management/', DeviceManagementView.as_view(), name='device_management'),
    
    
    


]
    

    



    
    

