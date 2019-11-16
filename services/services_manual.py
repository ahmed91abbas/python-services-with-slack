from services.utils.slack_message_builder import Slack_message_builder


class Services_manual:

    def __init__(self, *args):
        pass

    def build_response_message(self, action_list, **kwargs):

        smb = Slack_message_builder()
        smb.add_plain_section("List of available services:")
        smb.add_divider()
        smb.add_divider()
        for key, value in action_list.items():
            smb.add_formated_section(f'*{value["name"]}*')
            smb.add_plain_section(value["discription"])
            smb.add_plain_section('*Trigger regex (case ignored):* '
                                  + value["regex"])
            smb.add_divider()

        return smb.message
