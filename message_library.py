from rMoistPi.message.moisture_message import MoistureMessage

class MessageLibrary:
    available_messages = [
        MoistureMessage
    ]

    @staticmethod
    def get_library():
        return {c.message: c.get_response for c in MessageLibrary.available_messages}