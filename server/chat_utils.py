import json
import os
from dotenv import load_dotenv
import aiohttp

load_dotenv(override=True)

def get_text_message_body(recipient: str, text: str):
    return json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": text
        }
    })

# TODO - Message body should be dynamically generated based on template name selected.

def get_text_message_body_template(recipient: str):
    return json.dumps({
        "messaging_product": "whatsapp",
        "to": recipient,
        "recipient_type": "individual",
        "type": "template",
        "template": {
            "name": "demo_flow",
            "language": {
                "code": "en"
            },
            "components": [
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "image",
                            "image": {
                                "link": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRPVf8HVoBFpE0nFACC7y5IQqY_RVJq7K8t_w&s"
                            }
                        }

                    ]
                },
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "parameter_name": "service_name",
                            "text": "Engineer's PG"
                        }
                    ]
                }
            ]
        }
    })

async def send_message(message_body):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {os.getenv('WA_ACCESS_TOKEN')}"
        }
    async with aiohttp.ClientSession() as session:
        url = 'https://graph.facebook.com' + f"/{os.getenv('WA_API_VERSION')}/{os.getenv('PHONE_NUMBER_ID')}/messages"
        try:
            async with session.post(url, data=message_body, headers=headers) as response:
                if response.status == 200:
                    print("Status:", response.status)
                    print("Content-type:", response.headers['content-type'])

                    html = await response.text()
                    print("Body:", html)
                else:
                    print(response.status)        
                    print(response)        
        except aiohttp.ClientConnectorError as e:
            print('Connection Error', str(e))