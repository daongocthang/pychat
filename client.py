import argparse
import os
import socket
from sys import stdout, stdin
import threading
import time


class Send(threading.Thread):
    def __init__(self, sock):
        super().__init__()
        self.sock = sock

    def run(self):
        host = socket.gethostname()
        while True:
            print('>>', end='')
            stdout.flush()
            ipt = stdin.readline()[:-1]

            if ipt == 'QUIT':
                self.sock.sendall(' {} has left'.format(host).encode('ascii'))
                break
            else:
                self.sock.sendall('[{}] {}'.format(host, ipt).encode('ascii'))

        print('[+] shutting down...')
        self.sock.close()
        os._exit(0)


class Receive(threading.Thread):
    def __init__(self, sock):
        super().__init__()
        self.sock = sock

    def run(self):
        while True:
            try:
                msg = self.sock.recv(1024).decode('ascii')
                if msg:
                    print('\r[{}] {}\n>>'.format(time.strftime('%H:%M:%S'), msg), end='')
                else:
                    raise Exception()

            except:
                backspace = '\b' * 2
                print('{}[!] the client has lost connection to the server'.format(backspace))
                print('[+] shut down the client ')
                self.sock.close()
                os._exit(0)


class Client:
    def __init__(self, host, port):
        self.host = host.strip()
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        print('[+] trying to connect to {}:{}... '.format(self.host, self.port), end='')
        try:
            self.sock.connect((self.host, self.port))
        except:
            print('fail')
            os._exit(0)

        print('ok')
        print("[i] leave anytime by typing `QUIT`")

        send = Send(self.sock)
        recv = Receive(self.sock)

        # start send and receive threads
        send.start()
        recv.start()

        self.sock.sendall(' {} has joined'.format(socket.gethostname()).encode('ascii'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='chat server')
    parser.add_argument('host', help='Interface the server listens')
    parser.add_argument('-p', metavar='PORT', default=1060, type=int, help='TCP port (default=1060)')

    args = parser.parse_args()

    client = Client(args.host, args.p)
    client.start()
