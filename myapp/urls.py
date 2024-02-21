from django.urls import path
from .views import GetRTSPUrlView
from .views import test
from .views import CameraListAPIView,CameraDetailAPIView,CameraUpdateAPIView,CameraDeleteAPIView
from . import views
from myapp.views import CreateCameraView
# from device_discovery.views import fetch_devices
from .views import AudioStreamView
from .views import PTZControlView
from .views import PTZControlView
from .views import CreateCertificateView
from .views import DeviceManagementView
from .views import motion_detection_event



urlpatterns = [
    path('ptz_control/', PTZControlView.as_view(), name='ptz_control'),
    path('create-certificate/', CreateCertificateView.as_view(), name='create-certificate'),
    path('device-management/', DeviceManagementView.as_view(), name='device_management'),
    path('motion-detection-event/', motion_detection_event, name='motion_detection_event'),
    path('get/', GetRTSPUrlView.as_view(), name='get_rtsp_url'),
    path('create_camera/', CreateCameraView.as_view(), name='get_rtsp_url'),
    path('test', test, name='test'),
    path('create/', CameraListAPIView.as_view(),name='camera-create'),
    path('camera/get/', CameraDetailAPIView.as_view(), name='camera-detail'),
    path('camera/update/', CameraUpdateAPIView.as_view(),name='camera-update'),
    path('camera/delete/<int:pk>/', CameraDeleteAPIView.as_view(),name='camera-delete'),
    # path('fetch_devices/', fetch_devices, name='fetch_devices'),#device dicovery
    path('audio-stream/<str:camera_ip>/<str:username>/<str:password>/', AudioStreamView.as_view(), name='audio_stream'),
    
]
