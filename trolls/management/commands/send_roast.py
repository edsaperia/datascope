import socket
import json
from random import randint

from django.core.management.base import BaseCommand

from trolls.models.community import RedditScrapeCommunity


SOCKET_SERVER_ADDRESS = ('192.168.1.40', 8001)
SOCKET_LOCAL_ADDRESS = ('0.0.0.0', 8000)


class Command(BaseCommand):

    def handle(self, *args, **options):

        community = RedditScrapeCommunity.objects.get_latest_by_signature("RoastMe")
        data = community.get_growth("comments")
        posts = data.input.individual_set
        comments = data.output.individual_set

        posts_count = posts.all().count()
        random_index = randint(0, posts_count - 1)
        random_post = posts.all()[random_index]
        random_comment = comments.filter(identity=random_post["id"]).first()

        print('Random comment id={} comments={} '.format(random_post["id"], random_post["details_link"]))
        print('Random comment id={}'.format(random_comment["id"]))
        print('-' * 80)
        print(random_comment["comment"])
        return

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(SOCKET_LOCAL_ADDRESS)
        sock.listen(1)

        self.send_action(
            "Face.Detected",
            random_comment["comment"]
        )

        # Wait for a connection
        connection, client_address = sock.accept()
        try:
            # Receive the data in small chunks and retransmit it
            response = b""
            while True:
                data = connection.recv(16)
                if data:
                    response += data
                if data.endswith(b"\n"):
                    connection.sendall(b'ACK\n')
                    break
        finally:
            # Clean up the connection
            connection.close()
            sock.close()

        print(json.loads(response))

    def send_action(self, action, payload):  # TODO: decouple from command
        sock = socket.create_connection(SOCKET_SERVER_ADDRESS)
        message_data = {
            "command": action,
            "payload": payload
        }
        message = json.dumps(message_data).encode('utf-8')  # TODO: correct encoding for all types?
        sock.sendall(message)
        sock.close()
