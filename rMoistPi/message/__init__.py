from abc import ABC, abstractstaticmethod

class StandardMessage(ABC):
    topic: str
    delay: int

    @abstractstaticmethod
    def get_message():
        pass
