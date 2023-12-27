import socket
import threading
import os
import sys
import time
from getpass import getpass

nonvalid_ch = "é!'^+%&/()=?#<>£$½\\æ€¨':~@"
password = getpass("Password: ")
h = 1

is_exit = False
is_kicked = False
wrong_admin = False
is_banned = False
is_error = False
nick_taken = False

while True:
    if password == "1234":
        nickname = input("Nickname: ")
        i = 1
        is_valid = True
        while True:
            if nickname != "admin" and is_valid:
                if nickname[0] in "0123456789.":
                    is_valid = False
                for ch in nonvalid_ch:
                    if ch in nickname or len(nickname) < 3:
                        is_valid = False
                        break
                if is_valid:
                    break

            elif (i < 3) and (nickname == "admin" or not is_valid):
                print("You can not take this nickname. {} tries left.".format(3 - i))
                nickname = input("Nickname: ")
                is_valid = True
                i += 1

            else:
                print("You can not take this nickname. Try later.");
                time.sleep(1.5)
                quit()
        break

    elif password == "12admin34":
        nickname = "admin"
        break

    else:
        if (h < 3):
            print("Wrong password! {} tries left.".format(3 - h))
            password = getpass("Password: ")
            h += 1

        else:
            print("Wrong password! Try later.");
            time.sleep(1.5)
            quit()

server_ip = input("Enter server's IP: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((server_ip, 8113))


except:
    print("Could not connect with server.")
    time.sleep(1.5)
    quit()

def receive():
    global is_kicked
    global wrong_admin
    global is_banned
    global is_error
    global nick_taken

    while True:
        try:
            while True:

                message = client.recv(1024).decode('ascii')
                if message == "NICK":
                    client.send(nickname.encode('ascii'))
                    break

                elif message == "KICK":
                    client.send("KICKED".encode('ascii'))
                    print("You are kicked by admin!")
                    is_kicked = True
                    client.close()

                elif message == "OUT":
                    print("admin can not connect from another device.")
                    wrong_admin = True
                    quit()
                    client.close()

                elif message == "TAKEN":
                    print("Nickname is already taken.")
                    nick_taken = True
                    quit()
                    client.close()

                elif message == "BAN":
                    client.send("BANNED".encode('ascii'))
                    print("You are banned by admin!")
                    is_banned = True
                    client.close()

                else:
                    print(message)
                    break

        except:
            if not is_exit and not is_kicked and not wrong_admin and not is_banned and not nick_taken:
                print("An error occured!")
                is_error = True
            break

def write():

    global is_exit
    while True:
        try:
            if wrong_admin or is_banned or is_error or nick_taken or is_kicked:
                break

            msg = input()
            if msg== "quit":
                print("You have been logged out.")
                time.sleep(1.3)
                client.send("QUIT".encode('ascii'))
                is_exit = True
                client.close()

            if msg == '':
                continue

            message = '{}: {}'.format(nickname, msg)
            client.send(message.encode('ascii'))

        except:
            client.close()
            break

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
