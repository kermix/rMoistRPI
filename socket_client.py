import socket
import logging

from time import sleep

from message import Message
from exceptions import CloseConnection


class SocketClient():
    DEFAULT_PORT = 2137
    MAX_RETRIES = 3
    RETRY_DELAY = 15

    LOG_LEVEL = logging.INFO

    def __init__(self, host: str, port: int = DEFAULT_PORT, log_level: int = LOG_LEVEL):
        self._host = host
        self._port = port

        self._msg_library = None

        self._connection_closed = False

        logging.basicConfig(
            format="%(asctime)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=log_level,
        )

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def length(self):
        return self._length
    
    def set_message(self, msg: Message):
        self._msg = msg
    
    def connect(self):
        c = (self.host, self.port)

        retry = 0

        while retry < SocketClient.MAX_RETRIES and not self._connection_closed:
            try:
                with socket.socket() as client_socket:
                    client_socket.connect(c)

                    connection = Connection(client_socket, self._msg)
                    connection.run()
            except CloseConnection as ex:
                logging.error(ex)
                break
            except:
                retry += 1
                retry_delay = SocketClient.RETRY_DELAY*(retry)
                logging.error(f"Connection error. Retry {retry} from {SocketClient.MAX_RETRIES} in {retry_delay} seconds.")
                sleep(retry_delay)

    
class Connection():
    LENGTH = 1024

    def __init__(self, socket, message: Message):
        self._socket = socket
        self._msg = message

    def run(self):
        try:
            while True:
                self._socket.send(self._msg.encode()) 
                data = self._socket.recv(Connection.LENGTH).decode()

                if data == 'shutdown':
                    raise CloseConnection("Connection closed by a server")
                
                if not data:
                    raise CloseConnection("Connection closed. Cliend did not revieved any data")


                print('Received from server: ' + data)

                sleep(15)
        except KeyboardInterrupt:
            raise CloseConnection("Connection closed by a client")

if __name__ == "__main__":
    client = SocketClient("127.0.0.1")
    
    client.set_message('moisture')
    client.connect()


