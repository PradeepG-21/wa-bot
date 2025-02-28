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