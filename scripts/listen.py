#!/usr/bin/env python3

import socket
import select
import json
import time # for sleeping

# json_in -> json_out
def fsd(obj_in):
    keep_running = True

    # do stuff to json object
    print("In func f")
    for key, val in obj_in.items():
        print(key, val)

    obj_out = obj_in

    return obj_out, keep_running

# timeout is time for select to wait for input
# sleeptime is the time to sleep, so not polling constantly
def net(poll_func,receive_func,timeout_seconds=0.1,sleeptime_ms=900.0/1000.0):
    # create an INET, STREAMing socket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host, and a well-known port
    print(socket.gethostname())
    # allow reuse before binding
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind to localhost in end, nginx will interface with outside
    serversocket.bind(('', 2520))
    # become a server socket - can queue up to 5
    serversocket.listen(5)

    try:
        running = True
        while running:
            poll_func()
            time.sleep(sleeptime_ms)
            # block and wait for request
            #clientsocket, address = serversocket.accept()
            #print("Received conn from:",address)

            #print("Meh")

            potential_readers = [serversocket]
            potential_writers = []
            potential_errs = []
            time_out = timeout_seconds

            socks = []

            ready_to_read, ready_to_write, in_error = \
                    select.select(
                            potential_readers,
                            potential_writers,
                            potential_errs,
                            time_out)

            for s in ready_to_read:
                print("Bound")
                clientsocket, address = s.accept()
                socks.append(clientsocket)

            for clientsocket in socks:
                string_recv = clientsocket.recv(1024).decode()
                print("Received: (next line)")
                print(string_recv)

                try:
                    obj_recv = json.loads(string_recv)

                    obj_reply, keep_running = receive_func(obj_recv)
                    running = keep_running

                    json_reply = json.dumps(obj_reply)

                    string_reply = json_reply.encode()
                    clientsocket.send(string_reply)
                    print("Replying with: (next line)")
                    print(string_reply)
                except ValueError:
                    print("Could not interpret data as valid JSON")
                finally:
                    clientsocket.close()
                    socks.remove(clientsocket)
                    print("Closed conn")
    finally:
        print("Closing")
        try:
            serversocket.close()
        except UnboundLocalError:
            pass


def main():
    #net(fsd)
    pass

if __name__ == '__main__':
    main()
