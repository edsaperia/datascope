print('working')

import sys, os
sys.path.append("/Users/fako/Datascope/datascope")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "datascope.settings.development")


import socket
import json
from random import randint



SOCKET_SERVER_ADDRESS = ('192.168.1.40', 8001)
SOCKET_LOCAL_ADDRESS = ('0.0.0.0', 8002)


def send_action(action, payload):
    sock = socket.create_connection(SOCKET_SERVER_ADDRESS)
    message_data = {
        "command": action,
        "payload": payload
    }
    message = json.dumps(message_data).encode('utf-8')  # TODO: correct encoding for all types?
    sock.sendall(message)
    sock.close()


def get_random_comment():
    from trolls.models.community import RedditScrapeCommunity
    community = RedditScrapeCommunity.objects.get_latest_by_signature("RoastMe")
    data = community.get_growth("comments")
    posts = data.input.individual_set
    comments = data.output.individual_set

    posts_count = posts.all().count()
    random_index = randint(0, posts_count - 1)
    random_post = posts.all()[random_index]
    random_comment = comments.filter(identity=random_post["id"]).first()

    print('Random post id={} comments={} '.format(random_post["id"], random_post["details_link"]))
    print('Random comment id={}'.format(random_comment["id"]))
    print('-' * 80)
    print(random_comment["comment"])
    return random_comment["comment"]


def send_face_detected():
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(SOCKET_LOCAL_ADDRESS)
    sock.listen(1)

    send_action(
        "Face.Detected",
        get_random_comment()
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
    print('-' * 80)
    print(json.loads(response.decode('utf-8')))

