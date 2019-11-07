from services.utils.slack_message_builder import Slack_message_builder


class Services_manual:

    def __init__(self, *args):
        pass

    def build_response_message(self, action_list, **kwargs):

        smb = Slack_message_builder()
        for key, value in action_list.items():
            smb.add_formated_section(f'Service name: *{key}*')
            smb.add_plain_section(f'Regex: {value["regex"]}')
            smb.add_divider()

        return smb.message

