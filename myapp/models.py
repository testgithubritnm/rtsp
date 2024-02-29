from django.db import models


class Camera(models.Model):
      camera_name = models.CharField(max_length=100,unique=True,blank=False)
      ip = models.CharField(max_length=255,blank=False)
      port = models.IntegerField(default=80,blank=False)
      device_type = models.CharField(max_length=50,blank=True) 
      channel_number = models.IntegerField(default=1)  
      serial_number = models.CharField(max_length=50,blank=True)
      operation = models.CharField(max_length=50,blank=True)
      status = models.BooleanField(default=True,blank=True)
      device_model = models.CharField(max_length=50,blank=True)
      username = models.CharField(max_length=100,blank=True)
      password = models.CharField(max_length=100,blank=True)
      model = models.CharField(max_length=100,blank=True)
      serial_number = models.CharField(max_length=100,blank=True)
      firmware_version = models.CharField(max_length=100,blank=True)

      def __str__(self):
        return self.camera_name
    
class RTSPUrl(models.Model):
     url = models.CharField(max_length=255)

     def __str__(self):
        return self.url
    

    

      
      
      






    












    







