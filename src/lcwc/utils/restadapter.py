import aiohttp
from typing import Dict
from json import JSONDecodeError
from typing import List, Dict


class Result:
    def __init__(
        self,
        status_code: int,
        headers: Dict,
        message: str = "",
        url: str = "",
        data: List[Dict] = None,
    ):
        """
        Result returned from low-level RestAdapter
        :param status_code: Standard HTTP Status code
        :param message: Human readable result
        :param url: URL of the response
        :param data: Python List of Dictionaries (or maybe just a single Dictionary on error)
        """
        self.status_code = int(status_code)
        self.headers = headers
        self.message = str(message)
        self.url = url
        self.data = data if data else []


class RestException(Exception):
    pass


class RestAdapter:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        hostname: str = "",
        base: str = "",
        user_agent: str = "",
        ssl_verify: bool = True,
    ):
        """
        Constructor for RestAdapter
        :param session: Client session to use for requests
        :param hostname: Hostname of the API server
        :param base (optional): Base URL of the API server
        :param user_agent (optional):  User-Agent string to use when making HTTP requests
        :param ssl_verify: (optional) Verify SSL certificates. Defaults to True.
        :param logger: (optional) If your app has a logger, pass it in here.
        """
        self.session = session
        self.url = f"https://{hostname}/"

        if base:
            self.url = f"{self.url}{base}"

        self.user_agent = user_agent
        self._ssl_verify = ssl_verify
        if not ssl_verify:
            self.session.verify_ssl = False

    async def _do(
        self, http_method: str, endpoint: str, ep_params: Dict = None, data: Dict = None
    ) -> Result:
        """
        Private method for get(), post(), delete(), etc. methods
        :param http_method: GET, POST, DELETE, etc.
        :param endpoint: URL Endpoint as a string
        :param ep_params: Dictionary of endpoint parameters (Optional)
        :param data: Dictionary of data to pass in the request (Optional)
        :return: a Result object
        """
        full_url = self.url + endpoint

        headers = {}
        if self.user_agent:
            headers["User-Agent"] = self.user_agent

        try:
            response = await self.session.request(
                method=http_method,
                url=full_url,
                verify_ssl=self._ssl_verify,
                headers=headers,
                params=ep_params,
                json=data,
            )
        except aiohttp.ClientError as e:
            raise RestException("Request failed") from e

        # deserialize
        try:
            data_out = await response.json(content_type=None)
        except (ValueError, TypeError, JSONDecodeError) as e:
            raise RestException("Bad JSON in response") from e

        status_code = response.status
        # If status_code in 200-299 range, return success Result with data, otherwise raise exception
        is_success = 299 >= status_code >= 200  # 200 to 299 is OK
        if is_success:
            return Result(
                status_code,
                headers=response.headers,
                message=response.reason,
                url=response.url,
                data=data_out,
            )
        raise RestException(f"{status_code}: {response.reason}")

    async def get(self, endpoint: str, ep_params: Dict = None) -> Result:
        return await self._do(http_method="GET", endpoint=endpoint, ep_params=ep_params)

    async def post(
        self, endpoint: str, ep_params: Dict = None, data: Dict = None
    ) -> Result:
        return await self._do(
            http_method="POST", endpoint=endpoint, ep_params=ep_params, data=data
        )

    async def delete(
        self, endpoint: str, ep_params: Dict = None, data: Dict = None
    ) -> Result:
        return await self._do(
            http_method="DELETE", endpoint=endpoint, ep_params=ep_params, data=data
        )
