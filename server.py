import socket
import threading
import os


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

host = get_ip()

port = 8113
print("PID =", os.getpid())
print("IP =", get_ip())

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

class client:
    def __init__(self, ip, nickname, silenced, blocked):
        self.addr = str(ip).split("raddr=('")[1].split("'")[0]
        self.ip = ip
        self.nickname = nickname
        self.silenced = []
        self.blocked = []

clients = []
banned_ip = []
banned_nick = []


def broadcast(sender, message):
    global clients
    global banned_ip
    global banned_nick

    if message.decode("ascii").split()[1][0] == '!':
        target = message.split()[1].split()[0]
        i = 0

        for client in clients:
            if client.nickname == target[1:].decode('ascii'):
                if (client.nickname == "admin"):
                    sender.ip.send("admin can not be silenced!".encode('ascii'))

                else:
                    sender.silenced.append(client.nickname)
                    sender.ip.send("{} is silenced".format(client.nickname).encode('ascii'))
                i = 1

        if i == 0:
            sender.ip.send('User could not found'.encode('ascii'))

    elif message.decode("ascii").split()[1][0] == '$':
        target = message.split()[1].split()[0]
        i = 0

        for client in clients:
            if client.nickname == target[1:].decode('ascii'):
                if (client.nickname == "admin"):
                    sender.ip.send("admin can not be blocked!".encode('ascii'))

                else:
                    sender.blocked.append(client.nickname)
                    sender.ip.send("{} is blocked".format(client.nickname).encode('ascii'))
                i = 1

        if i == 0:
            sender.ip.send('User could not found'.encode('ascii'))

    elif message.decode("ascii").split()[1][0] == '>' and sender.nickname == "admin":
        target = message.split()[1].split()[0]
        if target[1:].decode('ascii') != "admin":
            i = 0

            for client in clients:
                if client.nickname == target[1:].decode('ascii'):
                    client.ip.send("KICK".encode('ascii'))
                    i = 1

            if i == 0:
                sender.ip.send('User could not found'.encode('ascii'))

    elif message.decode("ascii").split()[1][0] == '#' and sender.nickname == "admin":
        target = message.split()[1].split()[0]
        if target[1:].decode('ascii') != "admin":
            i = 0

            for client in clients:
                if client.nickname == target[1:].decode('ascii'):
                    client.ip.send("BAN".encode('ascii'))
                    i = 1

            if i == 0:
                sender.ip.send('User could not found'.encode('ascii'))

    elif message.decode("ascii").split()[1][0] == '\\':
        receiver = message.split()[1].split()[0]
        i = 0

        for client in clients:
            if client.nickname == receiver[1:].decode('ascii') and sender.nickname not in client.silenced and client.nickname not in sender.blocked:
                message = message.decode('ascii').replace("\\{} ".format(client.nickname), '')
                client.ip.send(message.encode('ascii'))
                i = 1

        if i == 0:
            sender.ip.send('User could not found'.encode('ascii'))

    else:
        for client in clients:
            if sender.nickname not in client.silenced  and client.nickname not in sender.blocked:
                if sender.nickname != client.nickname:
                    client.ip.send(message)

                else:
                    msg = message.decode('ascii').replace(sender.nickname, "You", 1)
                    client.ip.send(msg.encode('ascii'))


def handle(new_client):
    global clients
    while True:
        try:
            # Broadcasting Messages
            message = new_client.ip.recv(1024)
            if (message.decode('ascii') == "QUIT"):
                nc = new_client.nickname
                clients.remove(new_client)
                new_client.ip.shutdown(socket.SHUT_RDWR)
                print("{} left.".format(nc))

                if (len(clients) > 0):
                    for c in clients:
                        c.ip.send('{} left!'.format(nc).encode('ascii'))
                break

            elif (message.decode('ascii') == "KICKED"):
                nc = new_client.nickname
                clients.remove(new_client)
                new_client.ip.shutdown(socket.SHUT_RDWR)
                print("{} kicked.".format(nc))

                if (len(clients) > 0):
                    for c in clients:
                        c.ip.send('{} kicked by admin!'.format(nc).encode('ascii'))
                break

            elif (message.decode('ascii') == "BANNED"):
                nc = new_client.nickname

                if (new_client.addr != get_ip()) and (new_client.addr not in banned_ip):
                    banned_ip.append(new_client.addr)

                if nc not in banned_nick:
                    banned_nick.append(new_client.nickname)

                clients.remove(new_client)
                new_client.ip.shutdown(socket.SHUT_RDWR)
                print("{} banned.".format(nc))

                if (len(clients) > 0):
                    for c in clients:
                        c.ip.send('{} banned by admin!'.format(nc).encode('ascii'))
                break

            else:
                if message.decode('ascii') == "{}: ".format(new_client.nickname):
                    continue
                broadcast(new_client, message)


        except:

            nc = new_client.nickname
            if new_client in clients:
                clients.remove(new_client)
#            if (len(clients) > 0):
                for c in clients:
                    c.ip.send('{} left!'.format(nc).encode('ascii'))
            print('{} left.'.format(nc))
            break


def receive():
    while True:

        ip, address = server.accept()

        ip.send('NICK'.encode('ascii'))
        nick = ip.recv(1024).decode('ascii')

        if nick == "admin" and str(ip).split("raddr=('")[1].split("'")[0] != get_ip():
            ip.send("OUT".encode('ascii'))
            continue

        elif (str(ip).split("raddr=('")[1].split("'")[0] in banned_ip) or (nick in banned_nick):
            ip.send("BAN".encode('ascii'))
            continue

        is_taken = 0
        for clnt in clients:
            if nick == clnt.nickname:
                ip.send("TAKEN".encode('ascii'))
                is_taken = 1

        if is_taken == 1:
            continue

        new_client = client(ip, nick, [], [])
        clients.append(new_client)

        print("Connecting with {}...".format(str(address)))
        print("{} is connected.".format(nick))

        if (nick == "admin"):
            ip.send('Welcome admin.'.encode('ascii'))

        else:
            ip.send('Connected to server!'.encode('ascii'))

        for c in clients:
            if(nick != c.nickname):
                c.ip.send('{} is joined!'.format(nick).encode('ascii'))

        thread = threading.Thread(target=handle, args=(new_client,))
        thread.start()


receive()
