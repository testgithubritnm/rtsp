from rest_framework import serializers
from .models import Camera

class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = '__all__'
        
class RTSPUrlSerializer(serializers.Serializer):
    rtsp_url = serializers.CharField(max_length=200)

