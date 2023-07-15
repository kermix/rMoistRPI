from rMoistPi.socket_client import SocketClient
from rMoistPi.message.moisture_message import MoistureMessage

client = SocketClient("127.0.0.1")
    
client.set_message(MoistureMessage)
client.connect()