import os
from datetime import datetime
from hashlib import sha256

"""
This is a message class. It contains an easy to use framework for messages.
The working principal is the following:
    - Every message has a sender, a message part, and a way to tell, if the message contains a file.
    - If the message has a file, it has a name, and a content part.
    - Every part has a header, that is automatically created. (The length, with a given padding size)
    - Every message is able to validate itself. (with a given key)
    - Every message can create the stream to send, with a leading bit. (The number of parts in the message)
    - Every message can build up the file it contains, or is able to load in a file.
    - Every message has a function to create a readable version of itself. (Separating the sender, and the message.)
By runing this py file in itself, it will run a test to decide, if it's working correctly or not.
"""

class message():
    def __init__(self, has_file=False, HEADER_SIZE=10):
        """This function sets up the message object, depending on the input. Returns nothing.
        input: _has_file - boolean - Decides weather the message will contain a file, or not. (defailt is False)
               HEADER_SIZE - int - Sets up how many characers the header should be.
        """
        if has_file:
            self._file = None
            self._file_header = None
            self._file_name=None
            self._file_name_header=None
        self._has_file = has_file
        self._message = None
        self._message_header = None
        self.HEADER_SIZE = HEADER_SIZE
        self._sender = None
        self._sender_header = None
        self.set_date_time(str(datetime.date(datetime.now())), str(datetime.time(datetime.now())).split('.')[0])

    @property
    def message(self):
        """Returns the message in UTF-8 string format
        """
        return self._message.decode("utf-8")

    @message.setter
    def message(self, message):
        """Sets up the message, and the message header. Returns nothing.
        input: message - utf-8 string - This will be the message.
        """
        self._message = message.encode("utf-8")
        self._message_header = f"{len(self._message):>{self.HEADER_SIZE}}".encode("utf-8")

    @property
    def sender(self):
        """Returns the sender in UTF-8 string format
        """
        return self._sender.decode("utf-8")

    @sender.setter
    def sender(self, sender):
        """Sets up the sender, and the sender header. Returns nothing.
        input: sender - utf-8 string - This will be the sender's name.
        """
        self._sender = sender.encode("utf-8")
        self._sender_header = f"{len(self._sender):>{self.HEADER_SIZE}}".encode("utf-8")

    def set_file(self, path):
        """Sets up the file, red fro the 'path' variable. Returns nothing
        input: path - string (valid path) - Reads in the file located at the path.
        """
        with open(path, 'br') as f:
            self._file = f.read(-1)
        self._file_header = f"{len(self._file):>{self.HEADER_SIZE}}".encode("utf-8")
        _, self._file_name = os.path.split(path)
        self._file_name = self._file_name.encode("utf-8")
        self._file_name_header = f"{len(self._file_name):>{self.HEADER_SIZE}}".encode("utf-8")

    def create_file(self):
        """This function re-creates the file stored in the message to the following path: './files/{filename}' 
        Returns nothing.
        """
        with open(os.path.join("files", self._file_name.decode("utf-8")), 'bw') as f:
            f.write(self._file)

    def set_date_time(self, date, time):
        """Sets the message creation date and time
        Input:  date - string - The date of the message's creation
                time - string - the time of the message's creation
        """
        self.date = date.encode('utf-8')
        self.time = time.encode('utf-8')
        self.date_header = f"{len(self.date):>{self.HEADER_SIZE}}".encode('utf-8')
        self.time_header = f"{len(self.time):>{self.HEADER_SIZE}}".encode('utf-8')

    def get_date_time(self):
        """Returns the date-time in the following format:
        '{date} {time}' - '1998-09-21 12:00:00'
        """
        return f"{self.date.decode('utf-8')} {self.time.decode('utf-8')}"

    def get_message_formated(self, sep=": "):
        """Returns the message and the sender in a readable format with the separator character given. Example:
        sender: message - sep=': '
        input: sep - string - this string will be used to separate the sender from the message
        """
        return "{}{}{}".format(self._sender.decode("utf-8"), sep, self._message.decode("utf-8"))
    
    def __str__(self):
        return self.get_message_formated()

    def get_filename(self):
        """Returns the filename in UTF-8 string.
        """
        return self._file_name.decode("utf-8")

    def get_stream(self, send_sender=False):
        """Returns a byte stream in the following format: 
        '{leading_byte}{sender_header}{sender}{message_header}{message}{file_header}{file}{filename_header}{filename}'.
        Where the leading byte is decided by the number of elements sent (sender, message, file, filename).
        input: send_sender - boolean - decides wether to send the sender or not.
        """
        if self._message_header == None and self._has_file:
            self.message = f"Sent a file named '{self.get_filename()}'"
        if send_sender and self._sender_header != None: 
            if self._has_file and self._file != None:
                return b'6'+self.date_header+self.date+self.time_header+self.time+self._sender_header+self._sender+self._message_header+self._message+self._file_header+self._file+self._file_name_header+self._file_name
            return b'4'+self.date_header+self.date+self.time_header+self.time+self._sender_header+self._sender+self._message_header+self._message
        else:
            if self._has_file and self._file != None:
                return b'5'+self.date_header+self.date+self.time_header+self.time+self._message_header+self._message+self._file_header+self._file+self._file_name_header+self._file_name
            return b'3'+self.date_header+self.date+self.time_header+self.time+self._message_header+self._message
    
    def get_hash(self):
        """Returns the message's hash. The hash is created from the sender the message, and optionally the file, and filename, and their headers.
        """
        sum = self.date_header+self.date+self.time_header+self.time+self._sender_header+self._sender+self._message_header+self._message
        if self._has_file and self._file != None:
            sum += self._file_name_header+self._file_name+self._file_header+self._file
        sum = sha256(sum)
        return sum.hexdigest()

    def check_integrity(self, inc):
        """Returns wether the message's integrity is correct or not. 
        input: inc - sha256 key - Compares the message's key to this key
        """
        me = self.get_hash()
        return me == inc

if __name__=="__main__":
    msg = message(has_file=True)
    msg.message = "Test_message"
    msg.sender = 'Furry residency'
    msg.set_date_time('1998-09-21', '12:22:04')
    print("Hash: {} {}".format(msg.get_hash(), ("ok" if "5d942f554ca6e408cf7948bd3f664da409dd15451b98fc8c99fa58d4aece68d7" == msg.get_hash() else "ERROR")))
    msg2 = message(has_file=True)
    msg2.message = "Test_message"
    msg2.sender = 'Furry residency'
    msg2.set_date_time('1998-09-21', '12:22:04')
    print("Are they hash the same: {} {}".format(msg2.check_integrity(msg.get_hash()), ("ok" if msg2.check_integrity(msg.get_hash()) else "ERROR")))
    print("Message: {0} {2}\nSender: {1} {3}".format(msg.message, msg.sender, ("ok" if "Test_message" == msg.message else "ERROR"), ("ok" if "Furry residency" == msg.sender else "ERROR")))
    print(msg)
    print(msg.get_stream())
    if os.path.exists("SMALL_TEST.mid"):
        msg.set_file("SMALL_TEST.mid")
        msg.create_file()
    else:
        print("Small test file not found, test skipped!")
    if os.path.exists("BIG_TEST.sh"):
        msg.set_file("BIG_TEST.sh")
        msg.create_file()
    else:
        print("Big test file not fund, test skipped!")