#!/usr/bin/env python3

import socket
import select
import json
import time # for sleeping
import sys
import struct

# Specifically designed to read, write (intended to always be to the same socket)

class JsonSocket:

    def __init__(self, port): # port is 2520
        self._serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to a public host, and a well-known port
        print(socket.gethostname())
        # allow reuse before binding
        self._serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # bind to localhost in end, nginx will interface with outside
        self._serversocket.bind(('', port))
        # become a server socket - can queue up to n
        self._serversocket.listen(2)
        self._clientsocket = None

    def read(self, timeout = 0.2):
        potential_readers = [self._serversocket]
        potential_writers = []
        potential_errs = []

        ready_to_read, ready_to_write, in_error = \
                select.select(
                        potential_readers,
                        potential_writers,
                        potential_errs,
                        timeout)

        if in_error:
            print("Select error:", in_error)
            return None

        if ready_to_read:
            print("Ready to accept connection on socket")
            if self._clientsocket is not None:
                print("Closing old connection on:", self._clientsocket)
                self._clientsocket.close()
            # Can assume this won't block if select call passed - at least for
            # purposes of this here - not mission critical
            self._clientsocket, address = ready_to_read[0].accept()
            print(self._clientsocket, ",", address)

            print("Read incoming size")
            assert struct.calcsize("!I") == 4
            msg_size = struct.unpack("!I", tcp_read(self._clientsocket, 4))[0]
            print("Read message size as", msg_size, "bytes")

            print("Reading message")
            msg = tcp_read(self._clientsocket, msg_size).decode()
            print("Message read:", msg)

            print("Replying")

            return json.loads(msg)

        return None

    def write(self, json_out):
        try:
            # self._clientsocket.send((json_out + "END_OF_MESSAGE\n").encode())
            msg = json_out.encode()
            print("Writing out:", msg)
            self._clientsocket.sendall(msg)
            print("Done writing out msg")
        except Exception:
            raise
        finally:
            print("Closing", self._clientsocket)
            self._clientsocket.close()
            self._clientsocket = None

    # TODO: change to context manager "with"
    def close(self):
        if self._clientsocket is not None:
            self._clientsocket.close()
        self._serversocket.close()

def tcp_read(tcp_sock, msg_size):
    msg = bytearray()
    while msg_size > 0:
        chunk = tcp_sock.recv(msg_size)
        if len(chunk) == 0:
            break
        msg_size -= len(chunk)
        msg += chunk
    return bytes(msg)

def main(argv):
    port = 2520
    if len(argv) > 1:
        print("Receiver")
        js = JsonSocket(port)
        while True:
            data = js.read(2)
            if data:
                print("Got:", data)
                js.write(json.dumps(list(range(9))))
            else:
                print("Read nothing")
    else:
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect(('localhost', port))
        clientsocket.send(json.dumps({"hi": "there"}).encode())
        print(clientsocket.recv(1024))

if __name__ == '__main__':
    main(sys.argv)
