from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from onvif import ONVIFCamera
from zeep import Client
from onvif.exceptions import ONVIFError
# from django.shortcuts import rend
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from onvif import ONVIFService
import cv2
import numpy as np
import traceback
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from zeep import Client
from zeep.transports import Transport
from zeep.wsse.username import UsernameToken
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404 
import os
from onvif import ONVIFCamera, ONVIFError
from .models import Camera 
import urllib
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from django.utils.decorators import method_decorator
from .serializers import CameraSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from onvif import ONVIFCamera
# from myapp.models import ONVIFDevice  
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, StreamingHttpResponse, HttpResponseNotAllowed
from django.views import View
from wsdiscovery.discovery import ThreadedWSDiscovery as WSDiscovery
from wsdiscovery import Scope
import re
import logging
from zeep import Client
from .models import Camera, Certificate
from onvif.exceptions import ONVIFError
from django.views.decorators.csrf import csrf_protect


# get system date,time,year,hour
@csrf_exempt
def test(request):
                          
  mycam = ONVIFCamera('192.168.29.217', 80, 'admin', 'test123!', './pyenv/Lib/site-packages/wsdl/')
  resp = mycam.devicemgmt.GetHostname()
  print('My camera`s hostname: ' + str(resp.Name))
  dt = mycam.devicemgmt.GetSystemDateAndTime()
  tz = dt.TimeZone
  year = dt.UTCDateTime.Date.Year
  hour = dt.UTCDateTime.Time.Hour
  print("my camera timezone, ", hour, year, tz)
  return JsonResponse({'foo':'bar'})

#get RTSP URL
class GetRTSPUrlView(View):
    def get(self, request):
        try:
            print("1")
            print("Aboslute path ",os.path.abspath("./pyenv/Lib/site-packages/wsdl/"))
            # camera = ONVIFCamera('192.168.29.217', 80, 'admin', 'L2WOXHQK', os.path.abspath("./pyenv/Lib/site-packages/wsdl/"))
            
            camera = ONVIFCamera('192.168.29.217', 80, 'admin', 'L2WOXHQK', os.path.abspath("./pyenv/Lib/site-packages/wsdl/"))
            print("camera",camera)
            
            media_service = camera.create_media_service()
            print("media_service",media_service)

            profiles = media_service.GetProfiles()
            print("here 3")
            if not profiles:
                return JsonResponse({'error': 'No media profiles found'},status=500)
            media_profile_token = profiles[0].token
            
            print("token",media_profile_token)
            stream_setup = {
                'Stream': 'RTP-Unicast',  
                'Transport': {
                    'Protocol': 'UDP'  
                }
            }
            stream_uri_response = media_service.GetStreamUri({
                'ProfileToken': media_profile_token,
                'StreamSetup': stream_setup
            })
            if stream_uri_response and hasattr(stream_uri_response, 'Uri'):
                rtsp_url = stream_uri_response.Uri
                return JsonResponse({'rtsp_url': rtsp_url})
            else:
                return JsonResponse({'error': 'Failed to retrieve RTSP URL'}, status=500)

        except ONVIFError as e:
            return JsonResponse({'error': str(e)}, status=500)
        
     
#live streaming

from django.http import StreamingHttpResponse
from django.views.decorators import gzip
# from onvif import ONVIFCamera

# Import OpenCV module
import cv2

# Function to generate frames from camera feed
def gen_frames():
    # Open the default camera (0)
    # cap = cv2.VideoCapture('rtsp://192.168.29.53:8080/h264_ulaw.sdp')
    cap = cv2.VideoCapture('rtsp://admin:test123!@192.168.29.217:554/cam/realmonitor?channel=1&subtype=0')
  
    
    # Loop to continuously read frames from the camera
    while True:
        # Read a frame from the camera
        ret, frame = cap.read()
        
        # Check if the frame was successfully read
        if not ret:
            break
        
        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        
        # Yield the encoded frame as bytes
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    
    # Release the camera capture when done
    cap.release()

# Decorator to compress the response using gzip
@gzip.gzip_page
# View function for the home page
def home(request):
    try:
        # Return a streaming HTTP response with frames from the camera feed
        return StreamingHttpResponse(gen_frames(), content_type="multipart/x-mixed-replace;boundary=frame")
    except Exception as e:
        # Print an error message if an exception occurs
        print("An error occurred: ", e)
        
    
def test(request):
    print("test")

                         
   
    
    # camera models                                      
                                            
class CameraListAPIView(APIView):
    
    def get(self, request, pk=None):
        id = request.query_params.get('id')
        
        if id:
            camera = get_object_or_404(Camera, pk=id)
            serializer = CameraSerializer(camera)
            return Response(serializer.data)
        else:
            cameras = Camera.objects.all()
            serializer = CameraSerializer(cameras, many=True)
            return Response(serializer.data)
    def post(self, request):
        data = request.data
        serializer = CameraSerializer(data=data)

        if serializer.is_valid():
            existing_camera_with_name = Camera.objects.filter(camera_name=data['camera_name']).first()

            if existing_camera_with_name:
                return Response({'error': 'A camera with this name already exists.'}, status=status.HTTP_409_CONFLICT)
            else:
                camera_instance = serializer.save()
                response_data = {
                    "message": "Camera created successfully",
                    "camera": serializer.data
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CameraDetailAPIView(APIView):
     def get(self, request):
        id = request.query_params.get('id')

        if id:
            try:
                camera = Camera.objects.get(pk=id)
                serializer = CameraSerializer(camera)
                return Response(serializer.data)
            except Camera.DoesNotExist:
                return Response({'error': 'Camera with this ID does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'Please provide an ID query parameter'}, status=status.HTTP_400_BAD_REQUEST)
    
class  CameraUpdateAPIView(APIView):
    def put(self, request):
        camera_id = request.data.get('id', None)
        
        if camera_id is None:
            return Response({"error": "Please provide 'id' in the request body."}, status=status.HTTP_400_BAD_REQUEST)
        
        camera = get_object_or_404(Camera, pk=camera_id)
        serializer = CameraSerializer(camera, data=request.data,partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CameraDeleteAPIView(APIView):
    def delete(self, request, pk):
        camera = get_object_or_404(Camera, pk=pk)
        camera.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 
    
    
  

#device discovery 

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class FetchDevicesView(View):
    def get(self, request, *args, **kwargs):
        try:
            wsd = WSDiscovery()
            scope1 = Scope("onvif://www.onvif.org/Profile")
            wsd.start()
            services = wsd.searchServices(scopes=[scope1])
            ipaddresses = []
            for service in services:
                ipaddress = re.search('(\d+|\.)+', str(service.getXAddrs()[0])).group(0)
                ipaddresses.append(ipaddress)
                scopes = service.getScopes()
                logger.info(scopes)
            logger.info(f'Number of devices detected: {len(services)}')
            wsd.stop()
            return JsonResponse({'devices': ipaddresses})
        except Exception as e:
            logger.error(f'Error during device discovery: {e}')
            return JsonResponse({'error': 'An error occurred during device discovery'}, status=500)
                 
    def post(self, request, *args, **kwargs):
        try:
            data = request.POST.get('data')  

            if not data:
                return JsonResponse({'error': 'Data is required in the request'}, status=400)
            return JsonResponse({'message': 'POST request processed successfully'})
        except Exception as e:
            logger.error(f'Error during POST request: {e}')
            return JsonResponse({'error': 'An error occurred during POST request'}, status=500)

# ptz    

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect


@method_decorator(csrf_exempt, name='dispatch')
class PTZControlView(View):
    def __init__(self):
        super().__init__()
        self.ptz_control = ptzControl()

    def post(self, request, *args, **kwargs):
        try:
            
           
            pan = float(request.POST.get('pan', 0))
            tilt = float(request.POST.get('tilt', 0))
            zoom = float(request.POST.get('zoom', 0))
            velocity = float(request.POST.get('velocity', 1))

            self.ptz_control.move_continuous(pan, tilt)
            self.ptz_control.zoom(velocity)

            return JsonResponse({'status': 'PTZ control executed successfully'})
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {e}'}, status=500)

class ptzControl(object):
    def __init__(self):
        super(ptzControl, self).__init__()
        IP = "192.168.29.217"  
        PORT = 80  
        USER = "admin"  
        PASS = "L2WOXHQK"  

        self.mycam = ONVIFCamera(IP, PORT, USER, PASS)
        
        self.media = self.mycam.create_media_service()
       
        self.media_profile = self.media.GetProfiles()[0]
        
        token = self.media_profile.token
        
        self.ptz = self.mycam.create_ptz_service()
        
        request = self.ptz.create_type('GetServiceCapabilities')
        Service_Capabilities = self.ptz.GetServiceCapabilities(request)
        
        status = self.ptz.GetStatus({'ProfileToken': token})

       
        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.media_profile.PTZConfiguration.token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)

        self.requestc = self.ptz.create_type('ContinuousMove')
        self.requestc.ProfileToken = self.media_profile.token
        if self.requestc.Velocity is None:
            self.requestc.Velocity = self.ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position
            self.requestc.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
            self.requestc.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI

        
        self.requesta = self.ptz.create_type('AbsoluteMove')
        self.requesta.ProfileToken = self.media_profile.token
        if self.requesta.Position is None:
            self.requesta.Position = self.ptz.GetStatus(
                {'ProfileToken': self.media_profile.token}).Position
        if self.requesta.Speed is None:
            self.requesta.Speed = self.ptz.GetStatus(
                {'ProfileToken': self.media_profile.token}).Position

        self.requestr = self.ptz.create_type('RelativeMove')
        self.requestr.ProfileToken = self.media_profile.token
        if self.requestr.Translation is None:
            self.requestr.Translation = self.ptz.GetStatus(
                {'ProfileToken': self.media_profile.token}).Position
            self.requestr.Translation.PanTilt.space = ptz_configuration_options.Spaces.RelativePanTiltTranslationSpace[0].URI
            self.requestr.Translation.Zoom.space = ptz_configuration_options.Spaces.RelativeZoomTranslationSpace[0].URI
        if self.requestr.Speed is None:
            self.requestr.Speed = self.ptz.GetStatus(
                {'ProfileToken': self.media_profile.token}).Position

        self.requests = self.ptz.create_type('Stop')
        self.requests.ProfileToken = self.media_profile.token
        self.requestp = self.ptz.create_type('SetPreset')
        self.requestp.ProfileToken = self.media_profile.token
        self.requestg = self.ptz.create_type('GotoPreset')
        self.requestg.ProfileToken = self.media_profile.token
        self.stop()

    
    def stop(self):
        self.requests.PanTilt = True
        self.requests.Zoom = True
        print(f"self.request:{self.requests}")
        self.ptz.Stop(self.requests)

    
    def perform_move(self, requestc):
       
        ret = self.ptz.ContinuousMove(requestc)

    def move_tilt(self, velocity):
        self.requestc.Velocity.PanTilt.x = 0.0
        self.requestc.Velocity.PanTilt.y = velocity
        self.perform_move(self.requestc)

    def move_pan(self, velocity):
        self.requestc.Velocity.PanTilt.x = velocity
        self.requestc.Velocity.PanTilt.y = 0.0
        self.perform_move(self.requestc)

    def move_continuous(self, pan, tilt):
        self.requestc.Velocity.PanTilt.x = pan
        self.requestc.Velocity.PanTilt.y = tilt
        self.perform_move(self.requestc)

    def zoom(self, velocity):
        self.requestc.Velocity.Zoom.x = velocity
        self.perform_move(self.requestc)


    
    def move_abspantilt(self, pan, tilt, velocity):
        self.requesta.Position.PanTilt.x = pan
        self.requesta.Position.PanTilt.y = tilt
        self.requesta.Speed.PanTilt.x = velocity
        self.requesta.Speed.PanTilt.y = velocity
        ret = self.ptz.AbsoluteMove(self.requesta)

    
    def move_relative(self, pan, tilt, velocity):
        self.requestr.Translation.PanTilt.x = pan
        self.requestr.Translation.PanTilt.y = tilt
        self.requestr.Speed.PanTilt = [velocity,velocity]
       
        self.requestr.Speed.Zoom = 0
        ret = self.ptz.RelativeMove(self.requestr)

    def zoom_relative(self, zoom, velocity):
        self.requestr.Translation.PanTilt.x = 0
        self.requestr.Translation.PanTilt.y = 0
        self.requestr.Translation.Zoom.x = zoom
        self.requestr.Speed.PanTilt.x = 0
        self.requestr.Speed.PanTilt.y = 0
        self.requestr.Speed.Zoom.x = velocity
        ret = self.ptz.RelativeMove(self.requestr)

        

    def set_preset(self, name):
        self.requestp.PresetName = name
        self.requestp.PresetToken = '1'
        self.preset = self.ptz.SetPreset(self.requestp)  

    def get_preset(self):
        self.ptzPresetsList = self.ptz.GetPresets(self.requestc)

    def goto_preset(self):
        self.requestg.PresetToken = '1'
        self.ptz.GotoPreset(self.requestg)
        
    def get(self, request, *args, **kwargs):
        try:
            current_position = self.ptz_control.get_current_position()
            current_zoom = self.ptz_control.get_current_zoom()

            
            return JsonResponse({
                'current_position': current_position,
                'current_zoom': current_zoom,
                'status': 'GET request processed'
            })
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {e}'}, status=500)


        
 #audio
  
@method_decorator(csrf_exempt, name='dispatch')
class AudioStreamView(View):
    def get(self, request, camera_ip, username, password):
        return self.get_audio_stream(request, camera_ip, username, password)

    def post(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(['GET'])

    def get_audio_stream(self, request, camera_ip, username, password):
        
        cam = ONVIFCamera('192.168.29.217', 80, 'admin', 'L2WOXHQK')

        
        audio_sources = cam.media.GetAudioSources()

        if len(audio_sources) == 0:
            return HttpResponse("No audio sources found.")

        audio_source_token = audio_sources[0]._token

        
        media_service = cam.create_media_service()

        audio_configuration = media_service.GetAudioEncoderConfigurationOptions({'ProfileToken': 'MainProfile'})
        audio_configuration_token = audio_configuration[0]._token

        
        audio_stream_uri = media_service.create_media_service().GetStreamUri(
            {'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': 'UDP'},
             'ProfileToken': 'MainProfile',
             'SessionTimeout': 'PT0H0M10S'}) 

        audio_stream_uri = audio_stream_uri.Uri

        def audio_stream_generator():
            audio_stream = media_service.create_media_service().create_pull_point_subscription()
            audio_stream.SetSynchronizationPoint()

            while True:
                audio_data = audio_stream.PullMessages()
                yield audio_data

        return StreamingHttpResponse(audio_stream_generator(), content_type='audio/mpeg')
 
    


# create certificate

class CreateCertificateView(APIView):
    def post(self, request):
       
        camera = Camera.objects.first()  

       
        transport = Transport(timeout=10)
        client = Client('http://{}:{}/onvif/device_service'.format(camera.ip, camera.port), transport=transport)
       #client = Client('http://your_camera_ip:your_camera_port/onvif/device_service', transport=transport)
        
        client.transport.session.auth = (camera.username, camera.password)

        
        input_params = {
            'CertificateID': 'your_certificate_id',
            'Subject': 'your_subject',
            'ValidNotBefore': '2022-02-20T00:00:00',
            'ValidNotAfter': '2024-02-20T00:00:00'
        }

        response = client.service.CreateCertificate(**input_params)

        
        certificate_id = response.CertificateID
        certificate_base64 = response.Certificate.Data

       
        certificate = Certificate.objects.create(
            camera=camera,
            certificate_id=certificate_id,
            certificate_base64=certificate_base64
        )

        return JsonResponse({
            'certificate_id': certificate_id,
            'certificate_base64': certificate_base64
        })



#event handling 

@csrf_exempt
def motion_detection_event(request):
    if request.method == 'POST':
        try:
            
            cam_ip = 'your_camera_ip'
            cam_port = 80
            cam_username = 'your_camera_username'
            cam_password = 'your_camera_password'

            
            mycam = ONVIFCamera(cam_ip, cam_port, cam_username, cam_password)

            
            event_service = mycam.create_events_service()

            
            topic_filter = [
                ('tns1:VideoAnalytics/MotionDetection', 'http://www.onvif.org/ver10/topics'),
                ('tns1:VideoAnalytics/TamperingDetection', 'http://www.onvif.org/ver10/topics'),
                ('tns1:System/Alarm', 'http://www.onvif.org/ver10/topics')
            ]
            callback_url = 'http://your-django-app.com/motion-event-callback'  
            subscription_id = event_service.create_pull_point_subscription(topic_filter, callback_url)

            return HttpResponse(status=200)

        except ONVIFError as e:
            return HttpResponse(str(e), status=500)

    return HttpResponse('Method not allowed', status=405)


 
#device management

class DeviceManagementView(APIView):
    def get(self, request):
        try:
            
            cam_ip = 'your_camera_ip'
            cam_port = 80
            cam_username = 'your_camera_username'
            cam_password = 'your_camera_password'

            
            mycam = ONVIFCamera(cam_ip, cam_port, cam_username, cam_password)

            
            device_info = {
                'manufacturer': mycam.devicemgmt.GetManufacturer(),
                'model': mycam.devicemgmt.GetModel(),
                'firmware_version': mycam.devicemgmt.GetFirmwareVersion(),
                
            }

            return JsonResponse(device_info)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def post(self, request):
        try:
            
            cam_ip = 'your_camera_ip'
            cam_port = 80
            cam_username = 'your_camera_username'
            cam_password = 'your_camera_password'

            
            mycam = ONVIFCamera(cam_ip, cam_port, cam_username, cam_password)

        
            mycam.devicemgmt.SystemReboot()

            return JsonResponse({'message': 'Device rebooted successfully'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    






