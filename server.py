from socket_server import SocketServer

from message_library import MessageLibrary

if __name__ == "__main__":
    srv = SocketServer()
    lib = MessageLibrary.get_library()

    srv.set_message_library(lib)
    srv.run()
