from message import message
from datetime import datetime

def _retrive(client_socket, HEADERSIZE):
    message_header = client_socket.recv(1)
    if not len(message_header):
        return False
    ret = message(has_file=(int(message_header)==3 or int(message_header) == 4), HEADER_SIZE=HEADERSIZE)
    if (int(message_header)==2 or int(message_header) == 4):
        sender_length =   int(client_socket.recv(HEADERSIZE).decode("utf-8"))
        ret.set_sender(client_socket.recv(sender_length).decode("utf-8")) 
    message_length = int(client_socket.recv(HEADERSIZE).decode("utf-8"))
    ret.set_msg(client_socket.recv(message_length).decode("utf-8"))
    if ret.has_file:
        ret.file_header = client_socket.recv(HEADERSIZE)
        ret.file = client_socket.recv(int(ret.file_header.decode("utf-8")))
        ret.file_name_header = client_socket.recv(HEADERSIZE)
        ret.file_name = client_socket.recv(int(ret.file_name_header.decode("utf-8")))
    return ret

def retrive(client_socket, HEADERSIZE, name):
    validator = message(HEADER_SIZE=HEADERSIZE)
    validator.set_sender(name)
    validator.set_msg(str(datetime.timestamp(datetime.now())))
    key = validator.get_hash()
    if isinstance(_retrive(client_socket, HEADERSIZE), message): client_socket.send(f"1{int(len(key)/2):>{HEADERSIZE}}{key[:int(len(key)/2)]}".encode("utf-8"))
    else: return False
    if isinstance(_retrive(client_socket, HEADERSIZE), message): client_socket.send(f"1{int(len(key)/2):>{HEADERSIZE}}{key[int(len(key)/2):]}".encode("utf-8"))
    else: return False
    client_socket.send(validator.get_stream(True))
    resp = _retrive(client_socket, HEADERSIZE)
    return resp

def send(client_socket, HEADERSIZE, msg):
    now = datetime.now()
    key = msg.get_hash()
    outside_key = []
    client_socket.send(f"1{int(len(key)/2):>{HEADERSIZE}}{key[:int(len(key)/2)]}".encode("utf-8"))
    outside_key.append(_retrive(client_socket, HEADERSIZE))
    client_socket.send(f"1{int(len(key)/2):>{HEADERSIZE}}{key[int(len(key)/2):]}".encode("utf-8"))
    outside_key.append(_retrive(client_socket, HEADERSIZE))
    resp = _retrive(client_socket, HEADERSIZE)
    outside_key_full = outside_key[0].get_msg() + outside_key[1].get_msg()
    sent_at = datetime.fromtimestamp(float(resp.get_msg()))
    dif = (now - sent_at if sent_at < now else sent_at - now)    
    if resp.check_integrity(outside_key_full) and dif.seconds < 3:
        client_socket.send(msg.get_stream(True))
        return True
    else:
        msg.set_msg("Connection not secure")
        client_socket.send(msg.get_stream(True))
        return False
