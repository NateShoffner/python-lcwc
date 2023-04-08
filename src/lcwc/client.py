import aiohttp
from abc import ABC, abstractmethod
from lcwc.incident import Incident

class Client(ABC):

    def __init__(self) -> None:
        pass

    @abstractmethod
    async def fetch(self, session: aiohttp.ClientSession, timeout: int) -> bytes:   
        """ Gets the contents of the page and returns the contents as bytes """
        async with session.get(self.URL, timeout=timeout) as resp:
            if resp.status == 200:
                c = await resp.read()
                return c

    @abstractmethod
    def parse(self, contents: bytes) -> list[Incident]:
        """ Parses the contents of the page and returns a list of incidents """
        pass

    @abstractmethod
    def fetch_and_parse(self, session: aiohttp.ClientSession, timeout: int) -> list[Incident]:
        """ Fetches the page and parses the contents and returns a list of incidents """
        pass