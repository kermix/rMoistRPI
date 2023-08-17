import os
from typing import Optional
from dotenv import dotenv_values

from .misc import coalesce

class ClientConfig:
    DEF_PORT = 1883
    DEF_PREFIX = "homeassistant/"

    def __init__(self, 
                 broker: Optional[str] = None, 
                 port: Optional[int] = None, 
                 user: Optional[str] = None, 
                 password: Optional[str] = None):
        
        config = {
            **os.environ,
            **dotenv_values(".env")
        }

        self._broker = coalesce(broker, config.get("MQTT_BROKER"))
        self._port = coalesce(port, config.get("MQTT_PORT"), ClientConfig.DEF_PORT)
        self._user = coalesce(user, config.get("MQTT_USER"))
        self._password = coalesce(password, config.get("MQTT_PASSWORD"))

        self._prefix = coalesce(config.get("MQTT_PREFIX"), ClientConfig.DEF_PREFIX)

    @property
    def broker(self):
        return self._broker    

    @property
    def port(self):
        return self._port
    
    @property
    def user(self):
        return self._user
    
    @property
    def password(self):
        return self._password
    
    @property
    def prefix(self):
        return self._prefix
    
    def has_user_pass_auth(self):
        return self.user is not None and self.password is not None