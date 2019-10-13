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
        input: has_file - boolean - Decides weather the message will contain a file, or not. (defailt is False)
               HEADER_SIZE - int - Sets up how many characers the header should be.
        """
        if has_file:
            self.file = None
            self.file_header = None
            self.file_name=None
            self.file_name_header=None
        self.has_file = has_file
        self.message = None
        self.message_header = None
        self.HEADER_SIZE = HEADER_SIZE
        self.sender = None
        self.sender_header = None
        self.set_date_time(str(datetime.date(datetime.now())), str(datetime.time(datetime.now())).split('.')[0])
    
    def set_msg(self, message):
        """Sets up the message, and the message header. Returns nothing.
        input: message - utf-8 string - This will be the message.
        """
        self.message = message.encode("utf-8")
        self.message_header = f"{len(self.message):>{self.HEADER_SIZE}}".encode("utf-8")
    
    def get_msg(self):
        """Returns the message in UTF-8 string format
        """
        return self.message.decode("utf-8")

    def set_sender(self, sender):
        """Sets up the sender, and the sender header. Returns nothing.
        input: sender - utf-8 string - This will be the sender's name.
        """
        self.sender = sender.encode("utf-8")
        self.sender_header = f"{len(self.sender):>{self.HEADER_SIZE}}".encode("utf-8")

    def get_sender(self):
        """Returns the sender in UTF-8 string format
        """
        return self.sender.decode("utf-8")

    def set_file(self, path):
        """Sets up the file, red fro the 'path' variable. Returns nothing
        input: path - string (valid path) - Reads in the file located at the path.
        """
        with open(path, 'br') as f:
            self.file = f.read(-1)
        self.file_header = f"{len(self.file):>{self.HEADER_SIZE}}".encode("utf-8")
        _, self.file_name = os.path.split(path)
        self.file_name = self.file_name.encode("utf-8")
        self.file_name_header = f"{len(self.file_name):>{self.HEADER_SIZE}}".encode("utf-8")

    def create_file(self):
        """This function re-creates the file stored in the message to the following path: './files/{filename}' 
        Returns nothing.
        """
        with open(os.path.join("files", self.file_name.decode("utf-8")), 'bw') as f:
            f.write(self.file)

    def set_date_time(self, date, time):
        self.date = date.encode('utf-8')
        self.time = time.encode('utf-8')
        self.date_header = f"{len(self.date):>{self.HEADER_SIZE}}".encode('utf-8')
        self.time_header = f"{len(self.time):>{self.HEADER_SIZE}}".encode('utf-8')

    def get_date_time(self):
        return f"{self.date.decode('utf-8')} {self.time.decode('utf-8')}"

    def get_message_formated(self, sep=": "):
        """Returns the message and the sender in a readable format with the separator character given. Example:
        sender: message - sep=': '
        input: sep - string - this string will be used to separate the sender from the message
        """
        return "{}{}{}".format(self.sender.decode("utf-8"), sep, self.message.decode("utf-8"))
    
    def get_filename(self):
        """Returns the filename in UTF-8 string.
        """
        return self.file_name.decode("utf-8")

    def get_stream(self, send_sender=False):
        """Returns a byte stream in the following format: 
        '{leading_byte}{sender_header}{sender}{message_header}{message}{file_header}{file}{filename_header}{filename}'.
        Where the leading byte is decided by the number of elements sent (sender, message, file, filename).
        input: send_sender - noolean - decides wether to send the sender or not.
        """
        if self.message_header == None and self.has_file:
            self.set_msg(f"Sent a file named '{self.get_filename()}'")
        if send_sender and self.sender_header != None: 
            if self.has_file and self.file != None:
                return b'6'+self.date_header+self.date+self.time_header+self.time+self.sender_header+self.sender+self.message_header+self.message+self.file_header+self.file+self.file_name_header+self.file_name
            return b'4'+self.date_header+self.date+self.time_header+self.time+self.sender_header+self.sender+self.message_header+self.message
        else:
            if self.has_file and self.file != None:
                return b'5'+self.date_header+self.date+self.time_header+self.time+self.message_header+self.message+self.file_header+self.file+self.file_name_header+self.file_name
            return b'3'+self.date_header+self.date+self.time_header+self.time+self.message_header+self.message
    
    def get_hash(self):
        """Returns the message's hash. The hash is created from the sender the message, and optionally the file, and filename, and their headers.
        """
        sum = self.date_header+self.date+self.time_header+self.time+self.sender_header+self.sender+self.message_header+self.message
        if self.has_file and self.file != None:
            sum += self.file_name_header+self.file_name+self.file_header+self.file
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
    msg.set_msg("Test_message")
    msg.set_sender('Furry residency')
    msg.set_date_time('1998-09-21', '12:22:04')
    print("Hash: {} {}".format(msg.get_hash(), ("ok" if "5d942f554ca6e408cf7948bd3f664da409dd15451b98fc8c99fa58d4aece68d7" == msg.get_hash() else "ERROR")))
    msg2 = message(has_file=True)
    msg2.set_msg("Test_message")
    msg2.set_sender('Furry residency')
    msg2.set_date_time('1998-09-21', '12:22:04')
    print("Are they hash the same: {} {}".format(msg2.check_integrity(msg.get_hash()), ("ok" if msg2.check_integrity(msg.get_hash()) else "ERROR")))
    print("Message: {0} {2}\nSender: {1} {3}".format(msg.get_msg(), msg.get_sender(), ("ok" if "Test_message" == msg.get_msg() else "ERROR"), ("ok" if "Furry residency" == msg.get_sender() else "ERROR")))
    print(msg.get_message_formated())
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