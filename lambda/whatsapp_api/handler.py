import requests
from whatsapp_api.constants import WHATSAPP_API_URL


class WhatsAppApiHandler:
    def __init__(self,
                 token: str,
                 id: str):
        self._token = token
        self._id = id


    def handle_request(self,
                       method: str,
                       endpoint: str,
                       **kwargs) -> requests.request:
        accepted_methods = ['GET', 'POST']
        if method not in accepted_methods:
            raise Exception(f'Request method {method} is not accepted. '
                            f'Only {", ".join(accepted_methods)} are allowed')
        attempt = 0
        while attempt < 5:
            try:

                if 'headers' in kwargs:
                    kwargs['headers']['Authorization'] = f'Bearer {self._token}'
                else:
                    kwargs['headers'] = {'Authorization': f'Bearer {self._token}'}

                url = f'{WHATSAPP_API_URL}/{self._id}{endpoint}'
                print(f'[{method}] {url} - starting...')
                r = requests.request(
                    method=method,
                    url=url,
                    **kwargs
                )
                r.raise_for_status()
                print(f'[{method}] {url} - 200')
                return r
            except requests.exceptions.ReadTimeout:
                print(f'Attempt n {attempt}')
                attempt += 1
        raise Exception('There might be an connection error')
