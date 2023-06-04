import base64
import os
import ssl
import socket
import sys
from argparse import ArgumentParser
from getpass import getpass

import answer_parser
import message_creator


class SmtpClient:
    def __init__(self, server, port, mail_from, mail_to, subject,
                 need_verb, path, need_auth, ssl_available: bool, ):
        self.server = server
        self.port = port
        self.mail_from = mail_from
        self.mail_to = mail_to
        self.subject = subject
        self.verb = need_verb
        self.creator = message_creator.MimeMailCreator()
        self.auth = need_auth
        if need_auth:
            self.password = getpass()
        if ssl_available:
            try:
                low_sock = socket.create_connection((self.server, self.port))
                context = ssl.create_default_context()
                self.sock = context.wrap_socket(low_sock, server_hostname=self.server)
            except:
                print("Bad port")
                sys.exit()
        else:
            self.sock = socket.create_connection((self.server, self.port))
        self.path = path

    def start(self):
        self.creator.create_header(self.mail_from, self.mail_to, self.subject) \
            .create_text(f"Это картинки из папки {self.path}")
        for file in os.listdir(self.path):
            if file.endswith(('.jpg', '.jpeg', '.png', '.gif', '.tiff', '.webp')):
                self.creator.create_image(self.path + "/" + file)

        message = self.creator.get_message()
        self.receive_message()
        self.send_command("EHLO QWERTY\n")
        self.receive_message()

        if self.auth:
            self.send_command("auth login\n")
            self.receive_message()
            self.send_command(f'{base64.b64encode(self.mail_from.encode("utf-8")).decode("utf-8")}\n', )
            self.receive_message()
            self.send_command(f'{base64.b64encode(self.password.encode("utf-8")).decode("utf-8")}\n')
            self.receive_message()

        self.send_command(f'MAIL FROM: <{self.mail_from}>\nRCPT TO: <{self.mail_to}>\nDATA\n')
        self.receive_message()
        self.send_command(message)
        self.receive_message()

    def receive_message(self):
        message = self.sock.recv(1024).decode('utf-8')
        answer = answer_parser.Answer(message)
        if answer.last_code > 499:
            raise Exception(answer.all_messages)
        if self.verb:
            print(f'From server: {message}')

    def send_command(self, message):
        self.sock.send(message.encode("utf-8"))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--ssl', action='store_true', dest="need_ssl", required=False)
    parser.add_argument('-s', '--server', dest="server", type=str, required=True)
    parser.add_argument('-t', '--to', type=str, dest="to", required=True)
    parser.add_argument('-f', '--from', type=str, default='<>', dest='sender', required=False)
    parser.add_argument('--subject', type=str, dest="subject", default='Happy pictures', required=False)
    parser.add_argument('--auth', dest="need_auth", default=False, action='store_true')
    parser.add_argument('-v', '--verbose', dest="need_verb", action='store_true')
    parser.add_argument('-d', '--directory', dest="pictures_dir", type=str, default=os.getcwd(), required=False)
    args = parser.parse_args()
    server = args.server.split(":")
    if len(server) == 1:
        port = 25
        server = server[0]
    else:
        port = int(server[1])
        server = server[0]
    client = SmtpClient(server,
                        port,
                        args.sender,
                        args.to,
                        args.subject,
                        args.need_verb,
                        args.pictures_dir,
                        args.need_auth,
                        args.need_ssl,
                        )
    client.start()
