class Answer:
    def __init__(self, msg: str):
        self._parse_msg(msg)

    def _parse_msg(self, message: str):
        self.all_messages = message
        message_parts = message.split('\n')[:-1]
        self.last_code = int(message_parts[-1][0:4])
        self.last_msg = message_parts[-1][5:]

    def __str__(self):
        return self.all_messages
