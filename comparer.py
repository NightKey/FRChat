import message, pickle
with open("Test-client.msg", 'br') as f:
    client = f.read(-1).split(b"\t\t||\n")

with open("Test-server.msg", 'br') as f:
    server = f.read(-1).split(b"\t\t||\n")

for c, s in zip(client, server):
    tmp = pickle.loads(c)
    tmp2 = pickle.loads(s)
    print(tmp.check_integrity(tmp2.get_hash()))