from utils.slack_message_builder import Slack_message_builder
import youtube_dl
import subprocess
import os
import sys
import re
import uuid


class MyLogger(object):
    def __init__(self):
        self.msgs = []

    def debug(self, msg):
        self.msgs.append(msg)

    def warning(self, msg): pass

    def error(self, msg): pass


class Audio_fetcher:

    def __init__(self, env, *args):
        self.resources_folder = os.path.join(env("ROOT_PATH"), "resources")
        self.aud_folder = os.path.join(env("ROOT_PATH"), "downloads")

    def build_response_message(self, text, **kwargs):
        result = self.parse_message(text)

        if result["error"]:
            return result["message"]

        return {"upload_file":result["message"]}

    def parse_message(self, text):
        match = self.get_match("mp3 <?(http.*)>", text)
        if match:
            res = self.ydl_audios(match.group(1))
            return res
        return {"error":True, "message":"Failed to parse message"}

    def get_match(self, regex, text):
        p = re.compile(regex, re.IGNORECASE)
        return p.match(text)

    def ffmpeg_convert(self, in_file, out_file):
        # TODO support for linux
        _platform = sys.platform
        if _platform == "linux" or _platform == "linux2":
            print("Converting in Linux is not supported yet!")
        elif _platform == "win32" or _platform == "win64":
            ffmpeg_exe = os.path.join(self.resources_folder, "ffmpeg_win",
                                      "bin", "ffmpeg.exe")
            params = [ffmpeg_exe, '-i', in_file, out_file]
            subprocess.call(params, shell=False, close_fds=True)

    def ydl_audios(self, url):
        try:
            logger = MyLogger()
            filepath = os.path.join(self.aud_folder, str(uuid.uuid4()), '%(title)s.%(ext)s')
            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist': True,
                'outtmpl': filepath,
                'logger': logger,
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            msgs = logger.msgs
            for msg in msgs:
                if "[download] Destination: " in msg:
                    filename = msg[24:]
                    name = os.path.splitext(filename)[0]
                    extension = os.path.splitext(filename)[1]
                    if extension != ".mp3":
                        new_name = name + ".mp3"
                        self.ffmpeg_convert(filename, new_name)
                        os.remove(filename)
                        filename = new_name
                    break
            return {"error":False, "message":filename}
        except Exception as e:
            return {"error":True, "message":str(e)}
