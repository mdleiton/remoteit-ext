from django.core.mail import EmailMessage
from django.conf import settings
import syslog
import threading


class EmailWithTemplateThread(threading.Thread):
    def __init__(self, title, content, emails, filepath):
        self.title = title
        self.content = content
        self.emails = emails
        self.sent = False
        self.filepath = filepath
        threading.Thread.__init__(self)

    def run(self):
        try:
            email_list = []
            for email in self.emails:
                if email and "@" in email:
                    email_list.append(email)
            msg = EmailMessage(
                self.title, self.content, settings.EMAIL_HOST_USER, email_list
            )
            msg.content_subtype = "html"
            if isinstance(self.filepath, list):
                for file in self.filepath:
                    if isinstance(file, str):
                        msg.attach_file(file)
                    elif isinstance(file, dict):
                        msg.attach(**file)
                    else:
                        syslog.syslog("File type not supported")
            elif isinstance(self.filepath, str):
                msg.attach_file(self.filepath)
            elif isinstance(self.filepath, dict):
                msg.attach(self.filepath)
            else:
                syslog.syslog("File type not supported")
            msg.send()
            self.sent = True
            return True
        except Exception as e:
            self.sent = False
            syslog.syslog("Error sending email: " + str(e))
            msg = EmailMessage(
                "Error when sending emails to:" + str(email_list),
                self.title + self.content + str(e),
                settings.EMAIL_HOST_USER,
                [settings.ADMIN_MAIL],
                [],
                reply_to=[],
                headers={},
            )
            msg.send()
            return False