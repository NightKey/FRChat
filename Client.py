import socket
import select
import errno
import pickle

HEADERSIZE = 10
IP = "31.46.97.125"
PORT = 5465
UN = input("Username: ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

user_name = UN.encode('utf-8')
username_header = f"{len(user_name):<{HEADERSIZE}}".encode("utf-8")
client_socket.send(username_header+user_name)

while True:
    message = input(f"{UN} > ")
    if message:
        message = message.encode("utf-8")
        msg_header = f"{len(message):<{HEADERSIZE}}".encode("utf-8")
        client_socket.send(msg_header + message)
    try:
        while True:
            username_header = client_socket.recv(HEADERSIZE)
            if not len(username_header):
                print("Connection closed by the server")
                exit(0)
            username_length = int(username_header.decode("utf-8"))
            username = client_socket.recv(username_length).decode("utf-8")
            msg_header = int(client_socket.recv(HEADERSIZE).decode("utf-8"))
            msg = client_socket.recv(msg_header).decode("utf-8")
            print(f"{username}: {msg}")
    
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print("Reading error!")
            print(str(e))
            exit(0)
        continue
    except KeyboardInterrupt:
        print("Exiting...")
        exit(0)
    except Exception as e:
        print("General error")
        print(str(e))
        exit(0)