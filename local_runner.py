from environs import Env
import uuid
import random
import string
from datetime import datetime
import json
import tkinter as tk
import sys
import importlib
import glob
import re
import os


class Local_runner:

    def __init__(self):
        self.env = Env()
        self.env.read_env()
        self.services_dict = self.init_services_dict()
        self.default_values_file = "default_values.json"
        default_values = self.get_default_values()
        self.service_name = default_values["service_name"]
        self.message = default_values["message"]
        self.response = None
        self.create_gui()
        self.start_gui()

    def init_services_dict(self):
        services = {}
        root = "services"
        for filename in glob.glob(os.path.join(root, "*.py")):
            module_name = re.sub(r"\\+", ".", filename.replace(".py", ""))
            class_name = module_name.replace(f"{root}.", "").capitalize()
            key = ""
            for part in class_name.split("_"):
                key += f"{part.capitalize()} "
            key = key.strip()

            services[key] = {}
            services[key]["module_name"] = module_name
            services[key]["class_name"] = class_name

        return services

    def set_service_name(self, name):
        self.service_name = name

    def create_gui(self):
        font = ('calibri', 13)
        menufont = ('calibri', 16, 'bold')
        menufont1 = ('calibri', 16)
        self.bg_color = '#e6e6ff'

        self.root = tk.Tk()
        self.root.title("Local Runner")
        self.root.configure(background=self.bg_color)
        self.root.wm_protocol("WM_DELETE_WINDOW", self.on_close)

        self.options_frame = tk.Frame(self.root, bg=self.bg_color)
        self.message_frame = tk.Frame(self.root, bg=self.bg_color)
        self.action_frame = tk.Frame(self.root, bg=self.bg_color)
        self.response_label_frame = tk.Frame(self.root, bg=self.bg_color)
        self.response_frame = tk.Frame(self.root, bg=self.bg_color)

        self.options_frame.pack(pady=10)
        self.message_frame.pack(padx=10, pady=10)
        self.action_frame.pack(pady=10)
        self.response_label_frame.pack(padx=10)
        self.response_frame.pack(padx=10, pady=10)

        services_list = list(self.services_dict.keys())
        option = tk.StringVar()
        if self.service_name:
            option.set(self.service_name)
        else:
            option.set("Choose service name")
        self.options = tk.OptionMenu(self.options_frame,
                                     option,
                                     *services_list,
                                     command=self.set_service_name)
        self.options.config(bg=self.bg_color,
                            border=0,
                            highlightthickness=0,
                            compound=tk.CENTER,
                            activebackground=self.bg_color,
                            font=menufont)
        self.options["menu"].config(font=menufont1)
        self.options.pack()

        label = tk.Label(self.message_frame, text="Message:",
                         bg=self.bg_color, font=font)
        label.pack(side="left", padx=5)
        self.message_entry = tk.Entry(self.message_frame, width=65, font=font)
        self.message_entry.pack(side="left", padx=5)
        if self.message:
            self.message_entry.insert(0, self.message)
        self.message_entry.bind('<Return>', self.run_service)
        self.message_entry.focus()

        tk.Button(self.action_frame,
                  text="Clear window",
                  width=20,
                  height=2,
                  command=self.clear_window).pack(side="left", padx=20)

        button = tk.Button(self.action_frame,
                           text="Run Service",
                           width=20,
                           height=2,
                           command=self.run_service)
        button.pack(side="left", padx=20)

        label = tk.Label(self.response_label_frame, text="Response:",
                         bg=self.bg_color, font=font)
        label.pack(pady=5)
        self.response_text = tk.Text(self.response_frame,
                                     width=68,
                                     height=15,
                                     font=font)
        self.response_text.pack(side=tk.LEFT)
        scrollbar = tk.Scrollbar(self.response_frame,
                                 command=self.response_text.yview)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.response_text['yscrollcommand'] = scrollbar.set

    def start_gui(self):
        self.root.mainloop()

    def on_close(self):
        self.save_default_values()
        self.root.destroy()
        sys.exit()

    def clear_window(self):
        self.message_entry.delete(0, tk.END)
        self.response_text.delete('1.0', tk.END)

    def run_service(self, *args):
        self.response_text.delete('1.0', tk.END)
        self.message = self.message_entry.get()
        self.event = self.slack_event_mock(self.message)
        if self.service_name in self.services_dict:
            response = self.call_service()
            self.response_text.insert(tk.END, self.to_string(response))

    def get_default_values(self):
        try:
            with open(self.default_values_file) as json_file:
                data = json.load(json_file)
            return data
        except FileNotFoundError:
            default_values = {}
            default_values["service_name"] = None
            default_values["message"] = None
            return default_values

    def save_default_values(self):
        default_values = {}
        default_values["service_name"] = self.service_name
        default_values["message"] = self.message_entry.get()
        with open(self.default_values_file, 'w') as outfile:
            json.dump(default_values, outfile)

    def call_service(self):
        service_dict = self.services_dict[self.service_name]
        module = importlib.import_module(service_dict["module_name"])
        importlib.reload(module)

        service = getattr(module, service_dict["class_name"])(self.env)
        message = service.build_response_message(**self.event)
        return message

    def to_string(self, message):
        result = ""
        if type(message) is dict:
            for section in message["blocks"]:
                if section["type"] == "divider":
                    result += "-"*40 + "\n"
                else:
                    result += section["text"]["text"] + "\n"
        else:
            result = message
        return result

    def generate_random_alphanumeric(self, length):
        random_alphanumeric = ''.join(random.choice(
            string.ascii_uppercase +
            string.ascii_lowercase +
            string.digits) for _ in range(length))
        return random_alphanumeric

    def slack_event_mock(self, text):
        event = {}
        event["client_msg_id"] = str(uuid.uuid4())
        event["suppress_notification"] = False
        event["type"] = "message"
        event["text"] = text
        event["user"] = self.generate_random_alphanumeric(9)
        event["team"] = self.generate_random_alphanumeric(9)
        event["blocks"] = []

        block = {}
        block["type"] = "rich_text"
        block["block_id"] = self.generate_random_alphanumeric(5)
        block["elements"] = []

        element = {}
        element["type"] = "rich_text_section"
        element["elements"] = []

        inside_element = {}
        inside_element["type"] = "text"
        inside_element["text"] = text

        element["elements"].append(inside_element)
        block["elements"].append(element)
        event["blocks"].append(block)

        event["user_team"] = event["team"]
        event["source_team"] = event["team"]
        event["channel"] = self.generate_random_alphanumeric(9)
        event["event_ts"] = datetime.timestamp(datetime.now())
        event["ts"] = event["event_ts"]

        return event


if __name__ == '__main__':
    Local_runner()
