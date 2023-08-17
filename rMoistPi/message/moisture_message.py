from . import StandardMessage
import json

from grove.adc import ADC

from __main__ import client
import random

class GroveMoistureSensor:
    '''
    Grove Moisture Sensor class
    '''

    MOISTURE_SENSOR_PIN = 2

    def __init__(self, channel = None):
        if channel is None:
            channel = self.MOISTURE_SENSOR_PIN

        self.channel = channel
        self.adc = ADC(address = 0x08)

    @property
    def moisture(self):
        '''
        Get the moisture strength value/voltage

        Returns:
            (int): voltage, in mV
        '''
        value = self.adc.read_voltage(self.channel)
        return value


class MoistureMessage(StandardMessage):
    topic = 'sensor/rmoistpi_moist'
    delay = 1

    _min_readout, _max_readout = 1220, 2010

    config = {
        "device_class": "humidity", 
        "state_topic": "homeassistant/sensor/rmoistpi_moist/state", 
        "unit_of_measurement": "%", 
        "unique_id": "hum02ae", 
        "device": {"identifiers": ["rmoistpi02ae"], "name": "rMoistPi" }
    }
 
    @staticmethod
    def get_message():
        return round(MoistureMessage.read_moisture(), 2)
    
    @staticmethod
    def get_config_json():
        return json.dumps(MoistureMessage.config)

    @staticmethod
    def read_moisture():
        '''
        Reads the moisture strength value/voltage and converts it to the percentage scale

        Values below MoistureMessage._min_readout are equal to 0%. 
        Values over MoistureMessage._max_readout are equal to 100%

        Returns:
            (float): moisture, in %
        '''
        sensor = GroveMoistureSensor()
        measure = sensor.moisture

        if client.debug == True:
            random.seed()
            measure = random.randint(MoistureMessage._min_readout, MoistureMessage._max_readout)

        if measure > MoistureMessage._max_readout:
            return 0

        if measure < MoistureMessage._min_readout:
            return 100

        moisture = ((MoistureMessage._max_readout - measure)*100.0)/(MoistureMessage._max_readout-MoistureMessage._min_readout)

        return moisture
