import socket
import logging
import threading

class SocketServer:
    DEFAULT_HOST = ''
    DEFAULT_PORT = 2137
    REUSE_ADDRESS = True
    DEFAULT_N_LISTENERS = 1

    LENGHT = 1024

    LOG_LEVEL = logging.INFO
 
    def __init__(self, 
                 host: str = DEFAULT_HOST, 
                 port: int = DEFAULT_PORT, 
                 addr_reuse: bool = REUSE_ADDRESS,
                 log_level: int = LOG_LEVEL):
        self.host = host
        self.port = port
        self.addr_reuse = addr_reuse
        self._listener = SocketServer.DEFAULT_N_LISTENERS

        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=log_level)

    @property
    def listener(self):
        return self._listener
    
    def set_listeners(self, n_listeners: int):
        self.listener = n_listeners


    def run(self):
        with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as server_socket:
            if self.addr_reuse:
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            server_socket.bind((self.host, self.port)) 
            server_socket.listen(self.listener)

            logging.info(f"Server listens on {self.host}:{self.port}") 

            while True:
                conn, address = server_socket.accept()
                t = threading.Thread(target=self.client_connect, args=(conn, address))
                t.start()

    def client_connect(self, connectection, address):
        logging.info(f"Connection from {address} established") 
        while True:
            data = connectection.recv(self.LENGHT).decode()
            if not data:
                break
            print(f"from connected user {address}: {data}")
            data = input('Message to a client: ')
            connectection.send(data.encode())
    

class AnalogMoistureReader:
    pass



if __name__ == '__main__':
    srv = SocketServer()
    srv.run()