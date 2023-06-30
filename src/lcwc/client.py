from aiohttp import ClientSession


from abc import ABC, abstractmethod


class Client(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def get_incidents(self, session: ClientSession) -> list:
        pass
