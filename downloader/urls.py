from .views import *
from django.urls import path

urlpatterns = [
    path('', home, name='home'),
    path('get-url/', get_url,name='get_url'),
    path('download-video/', download_video,name='download_video'),
      
]

urlpatterns += [
     path("download-file/<str:file_id>/", serve_download, name="serve_download"),
 ]