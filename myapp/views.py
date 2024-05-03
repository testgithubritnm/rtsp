from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from onvif import ONVIFCamera
from zeep import Client
from onvif.exceptions import ONVIFError
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from onvif import ONVIFService
import cv2
import numpy as np
from datetime import datetime, timedelta
import traceback
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
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
from rest_framework import status
from django.http import JsonResponse
from django.http import HttpResponse, StreamingHttpResponse, HttpResponseNotAllowed
from django.views import View
import re
import logging
from zeep import Client
from onvif.exceptions import ONVIFError
from django.views.decorators.csrf import csrf_protect
from .serializers import RTSPUrlSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import StreamingHttpResponse
from onvif import ONVIFCamera, exceptions as onvif_exceptions 
from rest_framework import serializers
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import subprocess
from lxml import etree 
from django.http import StreamingHttpResponse, HttpResponse
from myapp.models import Camera
import cv2
import asyncio
import websockets
import cv2
import base64
import json
import numpy as np
from asgiref.sync import sync_to_async
from myapp.models import Camera
import imutils
import time
import subprocess



def gen_frames(rtsp_url_with_credentials):
    cap = cv2.VideoCapture(rtsp_url_with_credentials)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            break
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    cap.release()

def live_stream(request):
    camera_id = request.GET.get('id')
    if camera_id:
        try:
            camera = Camera.objects.get(id=camera_id)
            rtsp_url = camera.rtsp_url
            rtsp_url_with_credentials = add_credentials_to_rtsp_url(rtsp_url, camera)
            print("rtsp_url_with_credentials:", rtsp_url_with_credentials)
            return StreamingHttpResponse(gen_frames(rtsp_url_with_credentials), content_type="multipart/x-mixed-replace;boundary=frame")
        except Camera.DoesNotExist:
            return HttpResponse("Camera not found", status=404)
    else:
        return HttpResponse("Camera ID not provided", status=400)

def add_credentials_to_rtsp_url(rtsp_url, camera):
    username = camera.username
    password = camera.password
    if username and password:
        credentials = f"{username}:{password}@"
        return rtsp_url.replace("rtsp://", f"rtsp://{credentials}")
    else:
        raise ValueError("Username or password not provided for the camera")




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
        
        existing_camera_with_name = Camera.objects.filter(camera_name=data['camera_name']).first()
        if existing_camera_with_name:
            return Response({'error': 'A camera with this name already exists.'}, status=status.HTTP_409_CONFLICT)
        
        serializer = CameraSerializer(data=data)

        if serializer.is_valid():
            camera_instance = serializer.save()
            ip = camera_instance.ip
            port = camera_instance.port
            username = camera_instance.username
            password = camera_instance.password

            camera_onvif = ONVIFCamera(ip, port, username, password)
            media_service = camera_onvif.create_media_service()

            profiles = media_service.GetProfiles()
            if not profiles:
                return Response({'error': 'No media profiles found'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            media_profile_token = profiles[0].token

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
                camera_instance.rtsp_url = rtsp_url
                device_info = camera_onvif.devicemgmt.GetDeviceInformation()
                model = device_info.Model
                serial_number = device_info.SerialNumber
                firmware_version = device_info.FirmwareVersion
                camera_instance.model = model
                camera_instance.serial_number = serial_number
                camera_instance.firmware_version = firmware_version
                
                camera_instance.save()
                
                response_data = {
                    "message": "Camera created successfully",
                    "camera": serializer.data
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Failed to generate RTSP URL'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class CameraDetailAPIView(APIView):
    def get(self, request):
        id = request.query_params.get('id')

        cameras = Camera.objects.all()
        serializer = CameraSerializer(cameras, many=True)
        data = {'cameras': serializer.data}

        if id:
            try:
                camera = Camera.objects.get(pk=id)
                serializer_single = CameraSerializer(camera)
                data['single_camera'] = serializer_single.data
            except Camera.DoesNotExist:
                data['single_camera'] = None

        return Response(data)

    
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
    def delete(self, request):
        camera_id = request.data.get('id')  
        if not camera_id:
            return Response({'error': 'Camera ID not provided in the request body.'}, status=status.HTTP_400_BAD_REQUEST)

        camera = get_object_or_404(Camera, pk=camera_id) 
        camera.delete()  
        return Response({'message': 'Camera deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
  




def discover_devices(request):
    try:
        output = subprocess.check_output(['arp', '-a']).decode('utf-8')
        
        devices = []
        device_id_counter = 1  

        for line in output.split('\n'):
            if 'dynamic' in line.lower():
                parts = line.split()
                ip_address = parts[0]
                mac_address = parts[1]

                
                device_id = device_id_counter
                device_id_counter += 1

                devices.append({
                    'ip_address': ip_address,
                    'mac_address': mac_address,
                    'device_id': device_id
                })

        return JsonResponse({'devices': devices})
    except subprocess.CalledProcessError as e:
        return JsonResponse({'error': str(e)}, status=500)





async def process_video(websocket, path):
    try:
        print("Client connected.")

        message = await websocket.recv()
        data = json.loads(message)
        camera_id = data.get('id')

        if not camera_id:
            raise ValueError("Empty camera ID received")
        print("Received camera ID:", camera_id)

        camera = await sync_to_async(Camera.objects.get)(id=camera_id)

        rtsp_url_with_credentials = add_credentials_to_rtsp_url(camera.rtsp_url, camera)
        print("rtsp_url_with_credentials:", rtsp_url_with_credentials)

        cap = cv2.VideoCapture(rtsp_url_with_credentials)
        
        
        FRAMES_TO_PERSIST = 10 
        MIN_SIZE_FOR_MOVEMENT = 200 
        MOVEMENT_DETECTED_PERSISTENCE = 100 
        
        
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        
        first_frame = None
        next_frame = None

        
        font = cv2.FONT_HERSHEY_SIMPLEX
        delay_counter = 0
        movement_persistent_counter = 0

        while cap.isOpened():
            transient_movement_flag = False    
            ret, frame = cap.read()
            text = "Unoccupied"
            
            if not ret:
                print("CAPTURE ERROR")
                continue

            original_frame = frame.copy()

            frame = imutils.resize(frame, width=750)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            if first_frame is None: 
                first_frame = gray    

            delay_counter += 1

            if delay_counter > FRAMES_TO_PERSIST:
                delay_counter = 0
                first_frame = next_frame

                
            next_frame = gray

            frame_delta = cv2.absdiff(first_frame, next_frame)
            thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

            thresh = cv2.dilate(thresh, None, iterations=2)
            cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for c in cnts:
                (x, y, w, h) = cv2.boundingRect(c)
                if cv2.contourArea(c) > MIN_SIZE_FOR_MOVEMENT:
                    transient_movement_flag = True
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            if transient_movement_flag == True:
                movement_persistent_flag = True
                movement_persistent_counter = MOVEMENT_DETECTED_PERSISTENCE
     
            if movement_persistent_counter > 0:
                text = "Movement Detected " + str(movement_persistent_counter)
                movement_persistent_counter -= 1
            else:
                text = "No Movement Detected"

            
            (humans, _) = hog.detectMultiScale(frame, winStride=(10, 10), padding=(8, 8), scale=1.05)
            num_humans = len(humans)
            
            
            
            for (x, y, w, h) in humans:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                break
            frame_bytes = base64.b64encode(buffer)

            await websocket.send(json.dumps({"image": frame_bytes.decode(), "num_humans": num_humans, "motion_status": text}))

    except websockets.exceptions.ConnectionClosedError:
        print("Client disconnected. Waiting for a new connection...")
    except Camera.DoesNotExist:
        print("Camera not found")
    except Exception as e:
        print(f"Error on the server: {str(e)}")

def add_credentials_to_rtsp_url(rtsp_url, camera):
    username = camera.username
    password = camera.password
    if username and password:
        credentials = f"{username}:{password}@"
        return rtsp_url.replace("rtsp://", f"rtsp://{credentials}")
    else:
        raise ValueError("Username or password not provided for the camera")

async def server():
    start_server = websockets.serve(process_video, "localhost", 8001)  
    print("WebSocket server started.")
    await start_server
    
asyncio.get_event_loop().run_until_complete(server())
asyncio.get_event_loop().run_forever()




   











   







    



 

     


        


        











    
  


        









        






        







    









    
    


    


    

    






