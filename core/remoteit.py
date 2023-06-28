import binascii
import requests
import syslog
from requests_http_signature import HTTPSignatureAuth
from remote_ext import settings
from pexpect import *


class RemoteItConnection:
    def __init__(
        self,
        r3_secret_access_key,
        r3_access_key_id,
        api_key,
        url,
    ):
        self.url = url
        key = binascii.a2b_base64(r3_secret_access_key)
        self.auth = HTTPSignatureAuth(
            key=key, key_id=r3_access_key_id
        )
        self.headers = {
            "DeveloperKey": api_key,
            'host': "api.remote.it",
            'cache-control': "no-cache"
        }

    def list_devices(self):
        response = requests.get(
            self.url + "/device/list/all", auth=self.auth, headers=self.headers
        )
        if response.status_code == 200:
            return response.json()["devices"]
        else:
            raise Exception(
                "RemoteItConnection.list_devices. Error: %s" % response.text
            )

    def connect(
        self, deviceaddress
    ):
        response = requests.post(
            self.url + "/device/connect",
            json={
                "deviceaddress": deviceaddress,
                "wait": True,
            },
            auth=self.auth,
            headers=self.headers,
        )
        if response.status_code == 200:
            response = response.json()["connection"]
            return response
        else:
            raise Exception("Error: %s" % response.text)

    def close(self,deviceaddress, connectionid):
        response = requests.post(
            self.url + "/device/connect/stop",
            json={
                "deviceaddress": deviceaddress,
                "connectionid": connectionid, # from connection_data
            },
            auth=self.auth,
            headers=self.headers,
        )
        if response.status_code == 200:
            return True
        else:
            raise Exception("RemoteItConnection.close. Error: %s" % response.text)

    def download_file(self, username, password, deviceaddress, remote_file, save_as, timeout):
        connection_data = self.connect(deviceaddress)
        cwd = settings.DIR_TEMP
        scp_command = "scp -o StrictHostKeyChecking=no -P {}  {}@{}:{} {}{}".format(
            connection_data["proxyport"],
            username,
            connection_data["proxyserver"],
            remote_file,
            cwd,
            save_as,
        )
        try:
            child = spawn(scp_command, timeout=timeout)
            child.expect(
                "{}@{}'s password: ".format(username, connection_data["proxyserver"]), timeout=timeout
            )
            child.sendline(password)
            response = child.read()
            self.close(deviceaddress, connection_data["connectionid"])
            return response, str(cwd + save_as)
        except Exception as e:
            syslog.syslog("Error downloading file: " + str(e))
            return None, None

    def upload_file(self, username, password, deviceaddress, local_file, remote_file):
        connection_data = self.connect(deviceaddress)
        scp_command = "scp -o StrictHostKeyChecking=no -P {} {} {}@{}:{}".format(
            connection_data["proxyport"],
            local_file,
            username,
            connection_data["proxyserver"],
            remote_file,
        )
        child = spawn(scp_command)
        child.expect(
            "{}@{}'s password: ".format(username, connection_data["proxyserver"])
        )
        child.sendline(password)
        response = child.read()
        self.close(deviceaddress, connection_data["connectionid"])
        return response, remote_file

    def run_script(self, script, username, password, deviceaddress):
        connection_data = self.connect(deviceaddress)
        command = "ssh -o StrictHostKeyChecking=no -l {} {} -p {} {}".format(
            username,
            connection_data["proxyserver"],
            connection_data["proxyport"],
            script,
        )
        child = spawn(command)
        child.expect(
            "{}@{}'s password: ".format(username, connection_data["proxyserver"])
        )
        child.sendline(password)
        response = child.read()
        self.close(deviceaddress, connection_data["connectionid"])
        return response
