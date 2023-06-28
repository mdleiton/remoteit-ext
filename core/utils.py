import syslog
import os


def delete_file(file_path):
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            syslog.syslog("Removed file: " + file_path)
        else:
            syslog.syslog("File not found: " + file_path)
    except Exception as e:
        syslog.syslog("Error: Delete file: " + str(e))