import random

from typing import Optional

from paho.mqtt import client as mqtt_client

import socket
import ssl

import logging

import time

import threading

logging.basicConfig(level=logging.INFO)


from rMoistPi.client_config import ClientConfig


#TODO: project cleanup


    

class Client:
    def __init__(self, config: Optional[ClientConfig] = None):
        if config is None:
            config = ClientConfig()

        self._host = config.broker
        self._port = config.port 
        self._prefix = config.prefix 

        self.client = self.get_mqtt_connected_client(config)

    @property
    def client_id(self):
        return self._client_id
    
    @staticmethod
    def _on_connect(client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT Broker!")
        else:
            logging.error(f"Failed to connect, return code {rc}")

    def get_mqtt_connected_client(self, config: ClientConfig, use_ssl: bool=False):
        client_id = f"{socket.gethostname()}-{random.randint(0, 1000)}"

        client = mqtt_client.Client(client_id)
        
        if config.has_user_pass_auth():
            client.username_pw_set(config.user, config.password)

        if use_ssl:
            client.tls_set(certfile=None,
                keyfile=None,
                cert_reqs=ssl.CERT_REQUIRED)

        client.on_connect = Client._on_connect

        client.connect(config.broker, config.port)

        return client
    
    @staticmethod
    def publish_message(client, topic, message, delay):
        # while True:
            if callable(message):
                message = message()

            r = client.publish(topic, message)

            time.sleep(delay)

            #TODO: add signeled exit
            #TODO: publish_message should just publish message, the "looping logic" should be in a separate method

    def run(self, messages):
        client = self.client
        threads = []  

        client.loop_start()  
        for msg in messages:
            #TODO: refacator StandardMessage class and child classes
            topic = f"{self._prefix}{msg.message}/state"
            message = msg.get_response
            delay = msg.delay
            Client.publish_message(client,f"{self._prefix}{msg.message}/config", msg.get_config_json(), 0)
            thread = threading.Thread(target=Client.publish_message, args=(client, topic, message, delay))
            threads.append(thread)
            thread.start() 
        client.loop_stop()

if __name__ == '__main__':
    from rMoistPi.message.moisture_message import MoistureMessage
    c = Client()

    c.run([MoistureMessage])