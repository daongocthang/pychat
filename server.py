import argparse
import os
import socket
import threading
import time


class ClientThread(threading.Thread):
    def __init__(self, sc, sockname, server):
        super().__init__()
        self.sc = sc
        self.sockname = sockname
        self.server = server

    def run(self):
        while True:
            try:
                msg = self.sc.recv(1024).decode('ascii')
                if msg:
                    print('[{}]{}'.format(time.strftime('%H:%M:%S'), msg))
                    self.server.broadcast(msg, self.sockname)
                else:
                    raise Exception()

            except:
                print('[!] {} has closed the connection'.format(self.sockname[0]))
                self.sc.close()
                self.server.remove(self)
                return

    def send(self, msg):
        self.sc.sendall(msg.encode('ascii'))


class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.connections = []
        self.host = host
        self.port = port

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((self.host, self.port))
        except socket.error as e:
            print('[!]', e)
            os._exit(0)

        sock.listen(1)
        print('[+] listening at', sock.getsockname())
        while True:
            # waiting until accept new connection
            sc, sockname = sock.accept()
            print('[+] accept a new connection from {}'.format(sc.getpeername()))

            # create new thread
            clientthread = ClientThread(sc, sockname, self)

            # start new thread
            clientthread.start()

            # add thread to active connections
            self.connections.append(clientthread)
            print('[+] ready to receive messages from', sc.getpeername())

    def broadcast(self, msg, src):
        for conn in self.connections:
            # send to all connected clients except the source client
            if conn.sockname != src:
                conn.send(msg)

    def remove(self, connection):
        self.connections.remove(connection)


def commands(serv):
    while True:
        ipt = input('')
        if ipt == 'q':
            print('[+] closing all connections...')
            for conn in serv.connections:
                conn.sc.close()

            print('[+] shut down the server')
            os._exit(0)

        if ipt == 'thread-info':
            for i, t in enumerate(threading.enumerate()):
                print('[{}] {:.<20} {}'.format(i, t.name, 'working' if t.is_alive() else 'left'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('host')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060)

    args = parser.parse_args()
    serv = Server(args.host, args.p)
    serv.start()

    cmd = threading.Thread(target=commands, args=(serv,))
    cmd.start()
