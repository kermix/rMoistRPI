from . import StandardMessage
# from grove.grove_moisture_sensor import GroveMoistureSensor

from grove.adc import ADC

MOISTURE_SENSOR_PIN = 2

class GroveMoistureSensor:
    '''
    Grove Moisture Sensor class

    Args:
        pin(int): number of analog pin/channel the sensor connected.
    '''
    def __init__(self, channel):
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
    message = 'moisture'
    delay = 1

    @staticmethod
    def get_response():
        return MoistureMessage.read_moisture()

    @staticmethod
    def read_moisture():
        sensor = GroveMoistureSensor(MOISTURE_SENSOR_PIN)
        measure = sensor.moisture

        if measure < 1220:
            return "100%"

        moisture = ((2010 - measure)*100.0)/(2010-1220)
        return f"{moisture}%"
