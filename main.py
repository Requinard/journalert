import select
import json
import telepot
import os
from systemd import journal

class TelegramBackend:
    def __init__(self, config):
        self.config = config['telegram']
        self.bot = telepot.Bot(self.config['token'])

    def send(self, message):
        for recipient in self.config['recipients']:
            print("sending message to {0}".format(recipient))
            self.bot.sendMessage(recipient, message)

def create_poll(journal):
    p=select.poll()

    p.register(j, j.get_events())

    return p

def create_journal_reader():
    # Create a reader
    j = journal.Reader()
    j.this_boot()
    j.log_level(journal.LOG_INFO)

    # Set it to the back of the queue
    j.seek_tail()

    return j

def apply_config_to_journal(j, config):
    for entry in config['matchers']:
        j.add_match(_SYSTEMD_UNIT=entry['unit'])

    j.seek_tail

    return j

def parse_message(message):
    try:
        return "{0}: {1}".format(message['_SYSTEMD_UNIT'], message['MESSAGE']).strip()
    except KeyError:
        return "unknown: {0}".format(message['MESSAGE'])

def get_config():
    path = os.path.abspath(os.path.dirname(__file__))

    return json.loads(open(os.path.join(path, 'matchers.json'), 'r+').read())

if __name__ == '__main__':
    config = get_config()
    print(config)
    j = apply_config_to_journal(create_journal_reader(), config)
    poll = create_poll(journal)

    telegram = TelegramBackend(config)

    while True:
        if poll.poll(250):
            if j.process() == journal.APPEND:
                for entry in j:
                    telegram.send(parse_message(entry))
