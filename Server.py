import socket
import ssl
import select
from time import sleep
import sys
import roller, json, connector
from message import message
from logger import logger
import pickle
import os

HEADERSIZE = 10
IP = ""
PORT = 0
NAME = ""
out = None
debug = (False if sys.gettrace() == None else True)
del sys

def log(data):
    if debug:
        print(data)

def __init__():
    log('Initialisation started...')
    with open("server.ini", 'r') as f:
        data = json.load(f)
    log('Data red from ini file...')
    global IP
    global PORT
    global NAME
    global out
    global store_msgs
    IP = data['ip']
    PORT = data['port']
    NAME = data['name']
    store_msgs = bool(data['store'])
    log('Server data set...')
    out = logger(NAME)
    log('Logger set...')
    log('Initialisation finished...')

def send_welcome_message(client_socket):
    if store_msgs:
        log("Opening msg file...")
        with open(f"{NAME}.msg", 'rb') as f:
            log("Loading file content...")
            msgs = f.read(-1).split(b"\t\t||\n")
        for msg in msgs:
            if msg != b"":
                connector.send(client_socket, HEADERSIZE, pickle.loads(msg))
    else:
        pass

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #Binding to the socket
    server_socket.bind((IP, PORT))
    #Starting to listen on port
    server_socket.listen()

    if store_msgs and not os.path.exists(f"{NAME}.msg"):
        msg = message(HEADER_SIZE=HEADERSIZE)
        msg.set_sender(NAME)
        msg.set_msg("Server created")
        with open(f"{NAME}.msg", 'wb') as f:
            f.write(pickle.dumps(msg) + b"\t\t||\n")

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('certif/PrivateKey.pem', 'certif/PublicKey.pem')
    server_socket = context.wrap_socket(server_socket, server_side=True)

    socket_list = [server_socket]
    clients = {}
    EXIT = False
    try:
        while True:
            read_socket, _, exception_socket = select.select(socket_list, [], socket_list)
            
            for notified_socket in read_socket:            
                if notified_socket == server_socket:
                    client_socket, client_address = server_socket.accept()
                    log(f'Incoming connection from {client_address[0]} on {client_address[1]}')
                    try:
                        log("Retriving validator message...")
                        user = connector.retrive(client_socket, HEADERSIZE, NAME)
                        log('Validation message retrived....')
                    except Exception as ex:
                        out.log(f"Exception while retriving message: {ex}")
                        log(f"Exception while retriving message: {ex}")
                        user = False

                    if user is False:
                        log('Return value was false!')
                        continue
                    log('Adding client to client list...')
                    socket_list.append(client_socket)
                    clients[client_socket] = user.get_msg()
                    log('Generating notification message...')
                    msg = message(HEADER_SIZE=HEADERSIZE) 
                    msg.set_sender(NAME)
                    msg.set_msg(f"{user.get_msg()} connected to the server!")
                    log(f'Sending welcome message...\nStore messages: {store_msgs}')
                    send_welcome_message(client_socket)
                    if store_msgs:
                        log('Saving notification....')
                        with open(f"{NAME}.msg", 'ab') as f:
                            f.write(pickle.dumps(msg) + b"\t\t||\n")
                    log(f"{user.get_msg()} connected to the server!")

                    log('Sending notification message...')
                    for client_socket in clients:
                        connector.send(client_socket, HEADERSIZE, msg)
                    out.log(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user.get_msg()}")
                    log(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user.get_msg()}")

                else:
                    try:
                        log(f'Incoming message from {clients[notified_socket]}')
                        msg = connector.retrive(notified_socket, HEADERSIZE, NAME)
                    except:
                        out.log(f"Closed connection from {clients[notified_socket]}")
                        log(f"Closed connection from {clients[notified_socket]}")
                        socket_list.remove(notified_socket)
                        del clients[notified_socket]
                        continue
                    if "roll" in msg.get_msg():
                        value = roller.roller(msg.get_msg().replace("roll ", ''))
                        response = f"is rolled the followings: {value['rolled_values']}"
                        response += (f", with the modifyer {value['modifier_applied']}" if value["modifier_applied"] != None else "")
                        response += f". The total is {value['total']}."
                        msg.set_msg(response)                        

                    out.log(f"Retrived message from {msg.get_sender()}")
                    log(f"Retrived message from {msg.get_sender()}")
                    if store_msgs:
                        with open(f"{NAME}.msg", 'ab') as f:
                            f.write(pickle.dumps(msg) + b"\t\t||\n")
                    for client_socket in clients:
                        connector.send(client_socket, HEADERSIZE, msg)
            
            for notified_socket in exception_socket:
                socket_list.remove(notified_socket)
                del clients[notified_socket]
    except KeyboardInterrupt:
        EXIT = True
        out.log("User Interrupt")
    except Exception as e:
        out.log(e, error=True)
        log(e)
    finally:
        out.close()
        for s in socket_list:
            s.close()
        #socket_list[0].shutdown(socket.SHUT_RDWR)
        if EXIT:
            exit(0)

if __name__=="__main__":
    log('Logging enabled')
    __init__()
    log('Entering main loop...')
    while True:
        main()
        print('Restarting...')
