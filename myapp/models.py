from django.db import models
# from .models import Camera

class Camera(models.Model):
      camera_name = models.CharField(max_length=100,unique=True)
      ip = models.CharField(max_length=255)
      port = models.IntegerField(default=80)
      device_type = models.CharField(max_length=50) 
      channel_number = models.IntegerField()  
      serial_number = models.CharField(max_length=50)
      operation = models.CharField(max_length=50)
      status = models.BooleanField(default=True)
      device_model = models.CharField(max_length=50)
      username = models.CharField(max_length=100)
      password = models.CharField(max_length=100)

      def __str__(self):
        return self.camera_name
    
class Certificate(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    certificate_id = models.CharField(max_length=100)
    certificate_base64 = models.TextField()
      
      
      
#rtsp url
class RTSPStream(models.Model):
    rtsp_url = models.CharField(max_length=255)

    def __str__(self):
        return self.rtsp_url

class RTSPStreamCredentials(models.Model):
    rtsp_stream = models.OneToOneField(RTSPStream, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100, default='')

    def __str__(self):
        return f"Credential for {self.rtsp_stream.rtsp_url}"



class ONVIFDevice(models.Model):
    xaddr = models.CharField(max_length=255)  # Network address
    types = models.CharField(max_length=255)  # Service types
    scopes = models.CharField(max_length=255) # Service scopes

    def __str__(self):
        return f"ONVIFDevice - XAddr: {self.xaddr}"

class AudioFile(models.Model):
    title = models.CharField(max_length=100)
    audio_file = models.FileField(upload_to='audio_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class PTZControlHistory(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    pan = models.FloatField()
    tilt = models.FloatField()
    zoom = models.FloatField()

    @classmethod
    def create_history_entry(cls, pan, tilt, zoom):
        return cls.objects.create(pan=pan, tilt=tilt, zoom=zoom)


    

class Certificate(models.Model):
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    certificate_id = models.CharField(max_length=100)
    certificate_base64 = models.TextField()





