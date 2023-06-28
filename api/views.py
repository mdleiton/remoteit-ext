from core import remoteit
import json
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework import status
from remote_ext import settings
from core.task import device as device_tasks

@api_view(['GET'])
def list_devices_view(request):
    rc = remoteit.RemoteItConnection(
        settings.R3_SECRET_ACCESS_KEY,
        settings.R3_ACCESS_KEY_ID,
        settings.API_KEY,
        settings.URL_REMOTEIT,
    )
    list_devices = rc.list_devices()
    return JsonResponse({"results": list_devices})

@api_view(['GET'])
def generate_connection_view(request, deviceaddress):
    rc = remoteit.RemoteItConnection(
        settings.R3_SECRET_ACCESS_KEY,
        settings.R3_ACCESS_KEY_ID,
        settings.API_KEY,
        settings.URL_REMOTEIT,
    )
    connection_data = rc.connect(deviceaddress)
    return JsonResponse({"data": connection_data})

@api_view(['GET'])
def close_connection_view(request, connectionid, deviceaddress):
    rc = remoteit.RemoteItConnection(
        settings.R3_SECRET_ACCESS_KEY,
        settings.R3_ACCESS_KEY_ID,
        settings.API_KEY,
        settings.URL_REMOTEIT,
    )
    connection_data = rc.close(deviceaddress, connectionid)
    return JsonResponse({"data": connection_data})

@api_view(['POST'])
def download_file_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "INVALID DATA"}, status=status.HTTP_400_BAD_REQUEST)
    device_tasks.DownloadFile(data)
    return JsonResponse({"status": "ok"})


@api_view(['POST'])
def download_files_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "INVALID DATA"}, status=status.HTTP_400_BAD_REQUEST)
    device_tasks.DownloadFiles(data)
    return JsonResponse({"status": "ok"})