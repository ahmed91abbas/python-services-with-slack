from services.utils.slack_message_builder import Slack_message_builder
import re
import youtube_dl
import subprocess


class MyLogger(object):
    def __init__(self):
        self.msgs = []
    def debug(self, msg):
        self.msgs.append(msg)
    def warning(self, msg):pass
    def error(self, msg):pass

class Audio_fetcher:

    def __init__(self, env, *args):
        self.resources_folder = os.path.join(env("ROOT_PATH"), "resources")
        self.aud_folder = os.path.join(env("ROOT_PATH"), "downloads")

    def build_response_message(self, text, **kwargs):
        text = self.parse_message(text)

        smb = Slack_message_builder()
        smb.add_plain_section(text)

        return smb.message

    def parse_message(self, text):
        return text

    def ffmpeg_convert(self, in_file, out_file):
        #TODO support for linux
        _platform = sys.platform
        if _platform == "linux" or _platform == "linux2":
            print("Converting in Linux is not supported yet!")
        elif _platform == "win32" or _platform == "win64":
            ffmpeg_exe = os.path.join(self.resources_folder, "ffmpeg_win", "bin", "ffmpeg.exe")
            params = [ffmpeg_exe, '-i', in_file, out_file]
            subprocess.call(params, shell=False, close_fds=True)

    def ydl_audios(self, url):
        try:
            logger = MyLogger()
            filepath = os.path.join(self.aud_folder, '%(title)s.%(ext)s')
            ydl_opts = {
                'format': 'bestaudio/best',
                'noplaylist':True,
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
                    break
        except Exception as e:
            print(str(e))
