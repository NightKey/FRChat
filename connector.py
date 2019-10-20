from message import message
from datetime import datetime

"""This modul sends, and retrives messages in a 6 step way.
Send:
    1. Send first half of SHA256
    2. Retrive first half of SHA256
    3. Send secund half of SHA256
    4. Retrive secund half of SHA256
    5. Retrive message (validator message)
    6. Send message (If validator is within margin of error, and is correct)
Retrive:
    1. Retrive first half of SHA256
    2. Send first half of SHA256
    3. Retrive secund half of SHA256
    4. Send secund half of SHA256
    5. Send validator message
    6. Retrive message
it uses the message module!
"""

def _retrive(client_socket, HEADERSIZE):
    """Retrives a message with the following format: {size}[{sender_header}{sender}]{message_header}{message}[{file_header}{file}{file_name_header}{file_name}]
    Where the sender, and the file is optional, and dependent on the size. The posbble sizez:
        3 - message only (1, if date-time properties does not come!)
        4 - sender and message
        5 - message with file
        6 - sender, and message with file
    Input: client_socket - the socket it should retrive data from, HEADERSIZE - the header's size
    Return: a message object created from the socket stream
    """
    message_header = client_socket.recv(1)
    if not len(message_header):
        return False
    ret = message(has_file=(int(message_header)==5 or int(message_header) == 6), HEADERSIZE=HEADERSIZE)
    if int(message_header) != 1:
        date = client_socket.recv(int(client_socket.recv(HEADERSIZE).decode("utf-8"))).decode('utf-8')
        time = client_socket.recv(int(client_socket.recv(HEADERSIZE).decode("utf-8"))).decode('utf-8')
        ret.set_date_time(date, time)
    if (int(message_header)==4 or int(message_header) == 6):
        sender_length = int(client_socket.recv(HEADERSIZE).decode("utf-8"))
        ret.sender = client_socket.recv(sender_length).decode("utf-8")
    message_length = int(client_socket.recv(HEADERSIZE).decode("utf-8"))
    ret.message = client_socket.recv(message_length).decode("utf-8")
    if ret._has_file:
        ret._file_header = client_socket.recv(HEADERSIZE)
        ret._file = client_socket.recv(int(ret._file_header.decode("utf-8")))
        ret._file_name_header = client_socket.recv(HEADERSIZE)
        ret._file_name = client_socket.recv(int(ret._file_name_header.decode("utf-8")))
    return ret

def retrive(client_socket, HEADERSIZE, _validator):
    """Retrives a message with the described 6 step process.
    Input: client_socket - the socket used to communicate with the other party, HEADERSIZE - the header's size, _validator - the string that is used to validate.
    Return: a message object cretated from the socket stream
    """
    validator = message(HEADERSIZE=HEADERSIZE)
    validator.sender = _validator
    validator.message = str(datetime.timestamp(datetime.now()))
    key = validator.get_hash()
    if isinstance(_retrive(client_socket, HEADERSIZE), message): client_socket.send(f"1{int(len(key)/2):>{HEADERSIZE}}{key[:int(len(key)/2)]}".encode("utf-8"))
    else: return False
    if isinstance(_retrive(client_socket, HEADERSIZE), message): client_socket.send(f"1{int(len(key)/2):>{HEADERSIZE}}{key[int(len(key)/2):]}".encode("utf-8"))
    else: return False
    client_socket.send(validator.get_stream(True))
    resp = _retrive(client_socket, HEADERSIZE)
    return resp

def send(client_socket, msg):
    """Sends a message with the described 6 step process.
    Input: client_socket - the socket used to communicate with the other party, HEADERSIZE - the header's size, msg - the msg object to send.
    Return: True - message was sent safely, False - message was not sent, because the validation was not successfull (Error message was sent instead).
    """
    HEADERSIZE = msg.HEADERSIZE
    now = datetime.now()
    key = msg.get_hash()
    outside_key = []
    client_socket.send(f"1{int(len(key)/2):>{HEADERSIZE}}{key[:int(len(key)/2)]}".encode("utf-8"))
    outside_key.append(_retrive(client_socket, HEADERSIZE))
    client_socket.send(f"1{int(len(key)/2):>{HEADERSIZE}}{key[int(len(key)/2):]}".encode("utf-8"))
    outside_key.append(_retrive(client_socket, HEADERSIZE))
    resp = _retrive(client_socket, HEADERSIZE)
    outside_key_full = outside_key[0].message + outside_key[1].message
    sent_at = datetime.fromtimestamp(float(resp.message))
    dif = (now - sent_at if sent_at < now else sent_at - now)
    integ = resp.check_integrity(outside_key_full)
    if integ and dif.seconds <= 8:
        client_socket.send(msg.get_stream(True))
        return True
    else:
        msg.message = "Connection not secure"
        client_socket.send(msg.get_stream(True))
        return False
