from exceptions import SignaledExit

import logging
import signal
import socket
import threading


class SocketServer:
    DEFAULT_HOST = ""
    DEFAULT_PORT = 2137
    REUSE_ADDRESS = True
    DEFAULT_N_LISTENERS = 1

    LOG_LEVEL = logging.INFO

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        addr_reuse: bool = REUSE_ADDRESS,
        log_level: int = LOG_LEVEL,
    ):
        self.host = host
        self.port = port
        self.addr_reuse = addr_reuse
        self._listener = SocketServer.DEFAULT_N_LISTENERS

        logging.basicConfig(
            format="%(asctime)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            level=log_level,
        )

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
            with socket.socket(
                family=socket.AF_INET, type=socket.SOCK_STREAM
            ) as server_socket:
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
                client_connection_thread._end()
                client_connection_thread.join()

    def exit_call(self, signal_num, frame):
        logging.info(f"Exiting due to singal {signal_num}")
        raise SignaledExit


class ConnectionThread(threading.Thread):
    LENGHT = 1024

    def __init__(self, connection, address):
        self._exit_signal_event = threading.Event()

        self._connection = connection
        self._address = address

        threading.Thread.__init__(self, target=self._client_connect)

    @property
    def connection(self):
        return self._connection

    @property
    def address(self):
        return self._address

    def _client_connect(self):
        logging.info(f"Connection from {self.address} established")

        while not self._exit_signal_event.is_set():
            data = self.receive_message()

            if not data:
                break

            if data == "moisture":
                response = "0.1"
            else:
                response = "Unknown message"

            self.send_message(response)

        self._close_client_connection()

    def receive_message(self):
        message = None
        try:
            message = self.connection.recv(ConnectionThread.LENGHT).decode()
        except ConnectionResetError as ex:
            logging.info(f"Connection error for {self.address}: {ex} ")
            self._end()
        except Exception as ex:
            logging.info(
                f"Unexpected exception when trying to receive message from {self.address}: {ex}"
            )
            self._end()
        return message

    def send_message(self, message):
        try:
            self.connection.send(message.encode())
        except BrokenPipeError as ex:
            logging.info(f"Connection error for {self.address}: {ex}")
            self._end()

    def _close_client_connection(self):
        self.send_message("shutdown")
        self.connection.close()
        logging.info(f"Connection from {self.address} closed")

    def _end(self):
        self._exit_signal_event.set()