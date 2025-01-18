import base64

from utils.validators import is_base64
from whatsapp_api.handler import WhatsAppApiHandler


class Media(WhatsAppApiHandler):
    def __init__(self,
                 token: str,
                 id: str
                 ):
        super().__init__(token=token, id=id)
        self.resource_name = 'media'


    def upload(self,
                     base64_str: str,
                     content_type: str) -> dict:
        if not is_base64(base64_str):
            raise Exception('Não é um string base64')
        binary_data = base64.b64decode(base64_str)
        files = {
            "file": ("dummy", binary_data, content_type),
        }
        r = self.handle_request(
            method='POST',
            endpoint=f'/{self.resource_name}',
            timeout=2.5,
            files=files,
            data={'messaging_product': 'whatsapp'}
        )
        return r.json()