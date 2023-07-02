import socket
import logging
import threading
import signal


class SocketServer:
    DEFAULT_HOST = ''
    DEFAULT_PORT = 2137
    REUSE_ADDRESS = True
    DEFAULT_N_LISTENERS = 1

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
        
        signal.signal(signal.SIGTERM, self.exit_call)
        signal.signal(signal.SIGINT, self.exit_call)

        self._connection_threads = []


    @property
    def listener(self):
        return self._listener
    
    
    def set_listeners(self, n_listeners: int):
        self.listener = n_listeners


    def run(self):
        try:
            with socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM) as server_socket:
                if self.addr_reuse:
                    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                server_socket.bind((self.host, self.port)) 
                server_socket.listen(self.listener)

                logging.info(f"Server listens on {self.host}:{self.port}") 

                while True:
                    conn, address = server_socket.accept()
                    client_connection_thread = ConnectionThread(conn, address)
                    self._connection_threads.append(client_connection_thread)
                    client_connection_thread.start()

        except SignaledExit:
            for client_connection_thread in self._connection_threads:
                client_connection_thread.end()
                client_connection_thread.join()

    def exit_call(self, signal_num, frame):
        logging.info(f"Exiting due to singal {signal_num}")
        raise SignaledExit
    

class SignaledExit(Exception):
    pass


class ConnectionThread(threading.Thread):
    LENGHT = 1024

    def __init__(self, connection, address):
        self._exit_signal_event = threading.Event()
        threading.Thread.__init__(self, target=self._client_connect, args=(connection, address))       


    def _client_connect(self, connection, address):
        logging.info(f"Connection from {address} established") 

        while not self._exit_signal_event.is_set():
            # TODO: grecefully end on interupted connection / client exit
            data = connection.recv(ConnectionThread.LENGHT).decode()

            if not data:
                break

            if data == "moisture":
                response = '0.1'
            else:
                response = 'Unknown message'
                
            connection.send(response.encode())

        self._close_client_connection(connection, address)


    def _close_client_connection(self, connection, address):
        connection.send('shutdown'.encode())      
        connection.close()
        logging.info(f"Connection from {address} closed")


    def end(self):
        self._exit_signal_event.set()



if __name__ == '__main__':
    srv = SocketServer()
    srv.run()