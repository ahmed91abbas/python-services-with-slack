from utils.slack_message_builder import Slack_message_builder
import re
import nltk
try:
    nltk.data.find('tokenizers/wordnet')
except LookupError:
    nltk.download('wordnet')
from nltk.corpus import wordnet


class Dictionary:

    def __init__(self, *args):
        pass

    def get_word_information(self, text):
        syn = set()
        ant = set()
        synsets = wordnet.synsets(text)
        if not synsets:
            return {"error": True, "word": text}
        definition = synsets[0].definition()
        examples = synsets[0].examples()
        for synset in synsets:
            for lemma in synset.lemmas():
                syn.add(lemma.name())
                if lemma.antonyms():
                    ant.add(lemma.antonyms()[0].name())
        return {"error": False, "word": text, "definition": definition,
                "examples": examples, "synonyms": list(syn),
                "antonyms": list(ant)}

    def build_response_message(self, text, **kwargs):
        result = self.parse_message(text)

        if result["error"]:
            return "No results found for " + result["word"]

        smb = Slack_message_builder()
        smb.add_formated_section(f'*{result["word"]}*')
        smb.add_plain_section(result["definition"])
        smb.add_divider()

        if result["examples"]:
            smb.add_formated_section(
                '*Examples:*\n' + "\n".join(result["examples"]))
            smb.add_divider()

        if result["synonyms"]:
            smb.add_formated_section(
                f'*Synonyms:* {" ,".join(result["synonyms"])}')
            smb.add_divider()

        if result["antonyms"]:
            smb.add_formated_section(
                f'*Antonyms:* {" ,".join(result["antonyms"])}')
        return smb.message

    def get_match(self, regex, text):
        p = re.compile(regex, re.IGNORECASE)
        return p.match(text)

    def parse_message(self, text):
        m = self.get_match('(?:dict|dictionary) (.*)', text)
        if m:
            return self.get_word_information(m.group(1))
        return {"error": True, "word": text}
