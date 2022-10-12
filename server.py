import asyncio
from datetime import datetime
from http import client
import json
from socket import socket
import socketserver

import threading, time
from uuid import uuid1
import threading

game_data = {'componentsData': []}

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):

    def __init__(self, request, client_address, server) -> None:
        super().__init__(request, client_address, server)

    def handle(self):
        global game_data
        received_data = bytes(self.request[0]).decode().strip()
        size, command, message = received_data.split(';')

        current_thread = threading.current_thread()
        print(
            ">> {} [client {}]\n>> message_size: {} command: {}\n>> message:\n" \
            "{}\n" .format(current_thread.name, self.client_address, size, command, message)
        )

        response = None
        if command == 'get':
            game_data_str = json.dumps(game_data)
            game_data_str = f'{len(game_data_str)};{game_data_str}'
            response = str.encode(game_data_str)
        elif command == 'send':
            if int(size) == len(message):
                game_data = json.loads(message) 

            response = str.encode(received_data)
        
        socket = self.request[1]
        socket.sendto(response, self.client_address)

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = "127.0.0.1", 8888

    server = ThreadedUDPServer((HOST, PORT), ThreadedUDPRequestHandler)

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True

    try:
        server_thread.start()
        print("Server started at {} port {}".format(HOST, PORT))
        while True: time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        server.shutdown()
        server.server_close()
        exit()