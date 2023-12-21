from aiohttp import ClientSession


from abc import ABC, abstractmethod

from lcwc.incident import Incident


class Client(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    # TODO allow specification of timeout and incident categories
    @abstractmethod
    def get_incidents(self, session: ClientSession) -> list[Incident]:
        pass
