from datetime import datetime
import re
from services.utils.db_manager import Db_manager
from services.utils.slack_message_builder import Slack_message_builder

TABLE_NAME = "todo_list"
ID_COL = "generated_id"
TEXT_COL = "text"
CREATED_COL = "created_datetime"


class Todo_list:

    def __init__(self, env, *args):
        self.action_list = self.init_action_list()
        self.error_msg = None
        self.db = Db_manager(env("DB_FILE"), TABLE_NAME)

    def init_action_list(self):
        action_list = {}

        action_list["add_task"] = {}
        action_list["add_task"]["regex"] = 'add (.*) to todo'
        action_list["add_task"]["function"] = self.create_task
        action_list["add_task"]["success_message"] = \
            "Created a new task with ID %s"
        action_list["add_task"]["failed_message"] = \
            "Failed to create a new task"

        action_list["enumerate_all"] = {}
        action_list["enumerate_all"]["regex"] = \
            '(?:enumerate |list |show |all )?todo'
        action_list["enumerate_all"]["function"] = self.list_all_tasks
        action_list["enumerate_all"]["success_message"] = \
            "All tasks in Todo list:"
        action_list["enumerate_all"]["failed_message"] = \
            "Nothing to show. Todo list is empty."

        action_list["delete_task"] = {}
        action_list["delete_task"]["regex"] = \
            '(?:delete|remove) (\\d+) from todo'
        action_list["delete_task"]["function"] = self.delete_task
        action_list["delete_task"]["success_message"] = \
            "The task with ID %s has been removed successfully"
        action_list["delete_task"]["failed_message"] = \
            "Failed to remove the task"

        action_list["delete_all"] = {}
        action_list["delete_all"]["regex"] = \
            '(?:delete|remove) (?:all|everything) from todo'
        action_list["delete_all"]["function"] = self.delete_all_tasks
        action_list["delete_all"]["success_message"] = \
            "Deleted %s tasks. Todo list is empty now."
        action_list["delete_all"]["failed_message"] = \
            "Nothing to remove.Todo list is empty."

        return action_list

    def list_all_tasks(self):
        return self.db.select_all()

    def create_task(self, text):
        cols = [TEXT_COL, CREATED_COL]
        values = [text, datetime.now()]
        return self.db.insert_values(cols, values)

    def delete_task(self, task_id):
        return self.db.delete_where_condition(ID_COL, task_id)

    def delete_all_tasks(self):
        return self.db.delete_all()

    def excute_message_action(self, message):
        for action in self.action_list:
            p = re.compile(self.action_list[action]["regex"], re.IGNORECASE)
            m = p.match(message)
            if m:
                try:
                    text = m.group(1)
                except IndexError:
                    text = None

                if text:
                    return self.action_list[action],\
                        self.action_list[action]["function"](text)
                else:
                    return self.action_list[action],\
                        self.action_list[action]["function"]()
        failed = {}
        failed["failed_message"] = "Command not found!"
        return failed, None

    def build_response_message(self, text, **kwargs):

        action, results = self.excute_message_action(text)

        if self.error_msg:
            return self.error_msg

        smb = Slack_message_builder()

        if not results:
            smb.add_plain_section(action["failed_message"])
            return smb.message

        if type(results) is list:
            smb.add_plain_section(action["success_message"])
            for res in results:
                smb.add_formated_section(self.formate_cols(res))
        else:
            smb.add_plain_section(action["success_message"] % results)

        return smb.message

    def formate_cols(self, cols):
        task_id = cols[0]
        text = cols[1]
        ts = cols[2]

        ts = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S.%f')
        ts = ts.strftime("%Y-%m-%d %H:%M")

        text = f"{task_id} - *{text}* {ts}"
        return text
