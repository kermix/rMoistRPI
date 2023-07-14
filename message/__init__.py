from abc import ABC, abstractstaticmethod

class StandardMessage(ABC):
    message: str
    delay: int

    @abstractstaticmethod
    def get_response():
        pass
