from . import StandardMessage

class MoistureMessage(StandardMessage):
    message = 'moisture'
    delay = 15

    @staticmethod
    def get_response():
        return MoistureMessage.read_moisture()
    
    @staticmethod
    def read_moisture():
        return 'aaa'