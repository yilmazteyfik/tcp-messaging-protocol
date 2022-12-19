import socket
import sys
import threading

rendezvous = ('192.168.1.4', 55555)

print('connecting to rendezvous server')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 50009))
sock.sendto(b'0', rendezvous)

while True:
    data = sock.recv(1024).decode()

    if data.strip() == 'ready':
        print('checked in with server, waiting')
        break

data = sock.recv(1024).decode()

ip, sport, dport = data.split(' ')

sport = int(sport)
dport = int(dport)

print('\ngot peer')
print('     ip:              {}'.format(ip))
print('     source port:     {}'.format(sport))
print('     destination port:{}'.format(dport))

# punch hole

print('punching hole')
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', sport))
sock.sendto(b'0', (ip, dport))


print('ready to exchange messages\n')


def listen():
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(sport)
    sock1.bind(('0.0.0.0', sport))
    while True:
        data1 = sock1.recv(1024)
        print('\rpeer: {}\n> '.format(data1.decode()), end='')


listener = threading.Thread(target=listen, daemon=True);
listener.start()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', dport))

while True:
    msg = input('> ')
    sock.sendto(msg.encode(), (ip, sport))
