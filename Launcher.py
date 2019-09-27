import os, json

def save(path, stuff):
    with open(path, 'w') as f:
        json.dump(stuff, f)
    return stuff

def main():
    print("Checking for ini file...")
    if os.path.exists("server.ini"):
        is_server = True
    elif os.path.exists("client.ini"):
        is_server = False
    else:
        is_server = None
        print("No ini file found...")
        print("Initialising setup process...")

    if is_server:
        os.system("python server.py")
        exit(0)
    elif is_server is False:
        os.system("python Client_UI.py")
        exit(0)
    
    #Init creation
    server = None
    name = input('Please type in {} name: '.format(("the server's" if server else "your")))
    stuff = {'name':name, 'ip':('192.168.0.22' if server else 'chat.furryresidency.hu'), 'port':5465}
    print('Saving, and starting the program...')
    if server:
        save("server.ini", stuff)
        os.system("python server.py")
        exit(0)
    else:
        save("client.ini", stuff)
        os.system("python Client_UI.py")
        exit(0)
main()
