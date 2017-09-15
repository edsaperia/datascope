import socket
import json


SOCKET_SERVER_ADDRESS = ('192.168.1.40', 8001)
SOCKET_LOCAL_ADDRESS = ('0.0.0.0', 8000)


def send_action(action, payload):
    sock = socket.create_connection(SOCKET_SERVER_ADDRESS)
    message_data = {
        "command": action,
        "payload": payload
    }
    message = json.dumps(message_data).encode('utf-8')  # TODO: correct encoding for all types?
    sock.sendall(message)
    sock.close()


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(SOCKET_LOCAL_ADDRESS)
sock.listen(1)


# Wait for a connection
send_action(
    "Face.Detected",
    [
        "Your face is shinier than your future career.",
        "Only thing highbrow about you are your drawn-on eyebrows."
    ]
)
# Receive the data in small chunks and retransmit it
connection, client_address = sock.accept()
try:
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
