import socket
import ssl
import select
from time import sleep
import roller, json, connector
from message import message
from logger import logger

HEADERSIZE = 10
IP = ""
PORT = 0
NAME = ""
out = None
def __init__():
    with open("server.ini", 'r') as f:
        data = json.load(f)
    global IP
    global PORT
    global NAME
    global out
    IP = data['ip']
    PORT = data['port']
    NAME = data['name']
    out = logger(NAME)

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #Binding to the socket
    server_socket.bind((IP, PORT))
    #Starting to listen on port
    server_socket.listen()

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('certif/cert.pem', 'certif/key.pem')
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
                    try:
                        user = connector.retrive(client_socket, HEADERSIZE, NAME)
                    except Exception as ex:
                        out.log(f"Exception while retriving message: {ex}")
                        user = False

                    if user is False:
                        continue

                    socket_list.append(client_socket)
                    clients[client_socket] = user.get_msg()
                    msg = message(HEADER_SIZE=HEADERSIZE) 
                    msg.set_sender(NAME)
                    msg.set_msg(f"{user.get_msg()} connected to the server!")

                    for client_socket in clients:
                        connector.send(client_socket, HEADERSIZE, msg)
                    out.log(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user.get_msg()}")

                else:
                    try:
                        msg = connector.retrive(client_socket, HEADERSIZE, NAME)
                    except:
                        out.log(f"Closed connection from {clients[notified_socket]}")
                        socket_list.remove(notified_socket)
                        del clients[notified_socket]
                        continue
                    if "roll" in msg.get_msg():
                        value = roller.roller(msg.get_msg().replace("roll ", ''))
                        response = f"is rolled the followings: {value['rolled_values']}"
                        response += (f", with the modifyer {value['modifier_applied']}" if value["modifier_applied"] != None else "")
                        response += f". The total is {value['total']}."
                        msg.set_msg(response)                        

                    out.log(f"Retrived message from {msg.get_message_formated()}")

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
    finally:
        out.close()
        socket_list[0].close()
        #socket_list[0].shutdown(socket.SHUT_RDWR)
        if EXIT:
            exit(0)

if __name__=="__main__":
    __init__()
    while True:
        main()
        print('Restarting...')
