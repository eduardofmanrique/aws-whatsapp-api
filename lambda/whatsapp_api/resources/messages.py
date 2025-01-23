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

    def __base64_to_media(self, base64: str, content_type:str = 'application/pdf'):
        media_obj = Media(self._token, self._id)
        return media_obj.upload(base64_str=base64, content_type=content_type)['id']

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

    def send_document_message(self,
                              to: str,
                              base64_document: str,
                              document_filename: str,
                              caption: str,
                              recipient_type: str = 'individual'):
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "recipient_type": recipient_type,
            "type": "document",
            "document": {
                "id": self.__base64_to_media(base64_document),
                "caption": caption,
                "filename": document_filename
            }
        }
        r = self.handle_request(
            method='POST',
            endpoint=f'/{self.resource_name}',
            timeout=2.5,
            json=payload,
            headers={'Content-Type': "application/json"}
        )
        return r.json()

    def send_image_message(self,
                           to: str,
                           base64_image: str = None,
                           link: str = None,
                           caption: str = None,
                           content_type: str = "image/jpeg"):
        if not base64_image and not link:
            raise Exception("link or id of image is necessary")

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to,
            "type": "image",
            "image": {"link": link} if link else {"id": self.__base64_to_media(base64_image, content_type=content_type)}
        }

        if caption:
            payload["image"]["caption"] = caption

        r = self.handle_request(
            method='POST',
            endpoint=f'/{self.resource_name}',
            timeout=2.5,
            json=payload,
            headers={'Content-Type': "application/json"}
        )
        return r.json()
