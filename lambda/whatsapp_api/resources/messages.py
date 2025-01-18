from whatsapp_api.handler import WhatsAppApiHandler
from whatsapp_api.resources.media import Media


class Messages(WhatsAppApiHandler):
    def __init__(self,
                 token: str,
                 id: str
                 ):
        super().__init__(token=token, id=id)
        self.resource_name = 'messages'

    def __send_message_request(self, payload: dict):
        r = self.handle_request(
            method='POST',
            endpoint=f'{self.resource_name}',
            timeout=2.5,
            payload=payload
        )
        return r.json()

    def __base64_to_media(self, base64: str):
        media_obj = Media(self._token, self._id)
        return media_obj.upload(base64_str=base64, content_type='application/pdf')['id']

    def send_template_message(self,
                              to: str,
                              template_name: str,
                              template_language: str,
                              base64_document: str,
                              variables: list[dict] = None):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": template_language
                },
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "document",
                                "document": {
                                    "id": self.__base64_to_media(base64_document)
                                }
                            }
                        ]
                    }
                ]
            }
        }
        if variables:
            payload['template']['components'].append({'type': 'body', 'parameters': variables})

        r = self.handle_request(
            method='POST',
            endpoint=f'/{self.resource_name}',
            timeout=2.5,
            json=payload,
            headers={'Content-Type': "application/json"}
        )
        return r.json()