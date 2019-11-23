from utils.slack_message_builder import Slack_message_builder
'''
This is a skeleton class that should be used when adding
a new service to the Slackbot.
You will need to add this class to the action_list in the
main application "app.py"
'''


class New_service_skeleton:

    def __init__(self, *args):
        '''
        in the __init__ method you should accept any number
        of args in order to keep the main application "app.py"
        more generic. The arguments that are explicitly passed
        though the main application should be also passed explicitly
        in the argument to this method
        '''
        pass

    def build_response_message(self, text, **kwargs):
        '''
        This is the function that will be called from app.py.
        You can expose any Salck event argument like we did
        with the "text" argument here.
        This function should:
        - Parse the text to decide on actions and return message
        - Return either a string or a dict that is built with
        the Slack_message_builder class
        '''
        text = self.parse_message(text)

        smb = Slack_message_builder()
        smb.add_plain_section(text)

        return smb.message

    def parse_message(self, text):
        '''
        From here you should excute the core of this service
        and return whatever needed to build the return message
        in build_response_message method
        '''
        return text
