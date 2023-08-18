
import random
from typing import Optional, Iterable
from paho.mqtt import client as mqtt_client
import signal
import socket
import ssl
import time
import threading

from rMoistPi.misc import logger
from rMoistPi.client_config import ClientConfig
from rMoistPi.message import StandardMessage
from rMoistPi.exceptions import SignaledExit


class Client:
    def __init__(self, config: Optional[ClientConfig] = None, debug: bool = False):
        if config is None:
            config = ClientConfig()

        self._host = config.broker
        self._port = config.port
        self._prefix = config.prefix

        self._debug = debug

        self.client = self.get_mqtt_connected_client(config)

        signal.signal(signal.SIGTERM, self.exit_call)
        signal.signal(signal.SIGINT, self.exit_call)

        self._message_threads = []

        self._is_running = False

    @property
    def client_id(self):
        return self._client_id

    @property
    def debug(self):
        return self._debug

    @staticmethod
    def _on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT Broker!")
        else:
            logger.error(f"Failed to connect, return code {rc}")

    def get_mqtt_connected_client(self, config: ClientConfig, use_ssl: bool = False):
        client_id = f"{socket.gethostname()}-{random.randint(0, 1000)}"

        client = mqtt_client.Client(client_id)

        if config.has_user_pass_auth():
            client.username_pw_set(config.user, config.password)

        if use_ssl:
            client.tls_set(certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED)

        client.on_connect = Client._on_connect

        client.connect(config.broker, config.port)

        return client
    
    @staticmethod
    def publish_message(client: mqtt_client, topic: str, message: str, delay: int):
        if callable(message):
            message = message()

        r = client.publish(topic, message, retain=True)

    @staticmethod
    def i_publish_message(client: mqtt_client, topic: str, message: str, delay: int):
        while True:
            if callable(message):
                message = message()

            r = client.publish(topic, message)
            time.sleep(delay)

    def run(self, messages: Iterable[StandardMessage]):
        client = self.client
        self._is_running = True

        try:
            client.loop_start()
            for msg in messages:
                thread = MessageTread(client, msg, self._prefix)
                self._message_threads.append(thread)
                thread.start()

            for t in self._message_threads:
                t.join()

        except SignaledExit:
            for client_connection_thread in self._message_threads:
                client_connection_thread._end()
                client_connection_thread.join()
        finally:
            client.loop_stop()
            client.disconnect()
            self._is_running = False

        
    def exit_call(self, signal_num, frame):
        logger.info(f"Exiting due to singal {signal_num}")
        raise SignaledExit

class MessageTread(threading.Thread):
    def __init__(self, client, message, topic_prefix=""):
        self._exit_signal_event = threading.Event()

        self._client = client
        self._message = message

        self._topic_prefix = topic_prefix

        threading.Thread.__init__(self, target=self._client_connect)

    @property
    def client(self):
        return self._client

    def _client_connect(self):
        logger.info(f"Publishing message for {self._message.topic}")
        client = self._client

        client.publish(f"{self._topic_prefix}{self._message.topic}/config", self._message.get_config_json(), retain=True)                

        while not self._exit_signal_event.is_set():
            topic = f"{self._topic_prefix}{self._message.topic}/state"
            message = self._message.get_message()
            
            self.publish_message(topic, message)
            time.sleep(self._message.delay)

        self._close_client_connection()

    def publish_message(self, topic, message):
        client = self._client

        logger.info(f"Publishing message {message} for {topic}")

        client.publish(topic, message, retain = True)
        
    def _close_client_connection(self):
        logger.info(f"End publishing message for {self._message.topic}")

    def _end(self):
        self._exit_signal_event.set()
