import threading
from remote_ext import settings
from core import remoteit
from core import emails, utils


class DownloadFile(object):
    def __init__(self, data):
        thread = threading.Thread(target=self.run, args=())
        self.data = data
        thread.daemon = True
        thread.start()

    def run(self):
        rc = remoteit.RemoteItConnection(
            settings.R3_SECRET_ACCESS_KEY,
            settings.R3_ACCESS_KEY_ID,
            settings.API_KEY,
            settings.URL_REMOTEIT,
        )
        response, local_file = rc.download_file(
            username=self.data["username"],
            password=self.data["password"],
            deviceaddress=self.data["deviceaddress"],
            remote_file=self.data["remote_file"],
            save_as=self.data["save_as"],
            timeout=self.data["timeout"]
        )
        et = emails.EmailWithTemplateThread("Archivo de datos", "Archivo", self.data["emails"], [local_file])
        et.start()
        et.join()
        utils.delete_file(local_file)


class DownloadFiles(object):
    def __init__(self, data):
        thread = threading.Thread(target=self.run, args=())
        self.data = data
        thread.daemon = True
        thread.start()

    def run(self):
        rc = remoteit.RemoteItConnection(
            settings.R3_SECRET_ACCESS_KEY,
            settings.R3_ACCESS_KEY_ID,
            settings.API_KEY,
            settings.URL_REMOTEIT,
        )
        file_list = []
        for device in self.data["devices"]:
            response, local_file = rc.download_file(
                username=device["username"],
                password=device["password"],
                deviceaddress=device["deviceaddress"],
                remote_file=device["remote_file"],
                save_as=device["save_as"],
                timeout = device["timeout"]
            )
            if local_file:
                file_list.append(local_file)
        et = emails.EmailWithTemplateThread("Archivos de datos del SAT", "Archivos", self.data["emails"], file_list)
        et.start()
        et.join()
        for file_name in file_list:
            utils.delete_file(file_name)

