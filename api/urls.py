from django.urls import path
from api import views

urlpatterns = [
    path("list-devices/", views.list_devices_view),
    path("device/generate-connection/<deviceaddress>/", views.generate_connection_view),
    path("device/close-connection/<connectionid>/<deviceaddress>/", views.close_connection_view),
    path("device/download-file/", views.download_file_view),
    path("download-files/", views.download_files_view),
]