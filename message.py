import os
from hashlib import sha256

class message():
    def __init__(self, has_file=False, HEADER_SIZE=10):
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
    
    def set_msg(self, message):
        self.message = message.encode("utf-8")
        self.message_header = f"{len(self.message):>{self.HEADER_SIZE}}".encode("utf-8")
    
    def get_msg(self):
        return self.message.decode("utf-8")

    def set_sender(self, sender):
        self.sender = sender.encode("utf-8")
        self.sender_header = f"{len(self.sender):>{self.HEADER_SIZE}}".encode("utf-8")

    def get_sender(self):
        return self.sender.decode("utf-8")

    def set_file(self, path):
        with open(path, 'br') as f:
            self.file = f.read(-1)
        self.file_header = f"{len(self.file):>{self.HEADER_SIZE}}".encode("utf-8")
        _, self.file_name = os.path.split(path)
        self.file_name = self.file_name.encode("utf-8")
        self.file_name_header = f"{len(self.file_name):>{self.HEADER_SIZE}}".encode("utf-8")

    def create_file(self):
        with open(os.path.join("files", self.file_name.decode("utf-8")), 'bw') as f:
            f.write(self.file)

    def get_message_formated(self, sep=": "):
        return "{}{}{}".format(self.sender.decode("utf-8"), sep, self.message.decode("utf-8"))
    
    def get_stream(self, server=False):
        if server and self.sender_header != None: 
            if self.has_file and self.file != None:
                return b'4'+self.sender_header+self.sender+self.message_header+self.message+self.file_header+self.file+self.file_name_header+self.file_name
            return b'2'+self.sender_header+self.sender+self.message_header+self.message
        else:
            if self.has_file and self.file != None:
                return b'3'+self.message_header+self.message+self.file_header+self.file+self.file_name_header+self.file_name
            return b'1'+self.message_header+self.message
    
    def get_hash(self):
        sum = self.sender_header+self.sender+self.message_header+self.message
        if self.has_file and self.file != None:
            sum += self.file_name_header+self.file_name+self.file_header+self.file
        sum = sha256(sum)
        return sum.hexdigest()

    def check_integrity(self, inc):
        me = self.get_hash()
        return me == inc

if __name__=="__main__":
    msg = message(has_file=True)
    msg.set_msg("Test_message")
    msg.set_sender('Furry residency')
    print("Hash: {} {}".format(msg.get_hash(), ("ok" if "a3ce2b8e07d3a1e8b0263e783f4b401e0910ad50c71e40a9004151d324ad13ab" == msg.get_hash() else "ERROR")))
    msg2 = message(has_file=True)
    msg2.set_msg("Test_message")
    msg2.set_sender('Furry residency')
    print("Are they hash the same: {} {}".format(msg2.check_integrity(msg.get_hash()), ("ok" if msg2.check_integrity(msg.get_hash()) else "ERROR")))
    print("Message: {0} {2}\nSender: {1} {3}".format(msg.get_msg(), msg.get_sender(), ("ok" if "Test_message" == msg.get_msg() else "ERROR"), ("ok" if "Furry residency" == msg.get_sender() else "ERROR")))
    print(msg.get_message_formated())
    print(msg.get_stream())
    msg.set_file("SMALL_TEST.mid")
    msg.create_file()
    msg.set_file("BIG_TEST.sh")
    msg.create_file()