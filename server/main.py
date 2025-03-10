import os
from dotenv import load_dotenv
import logging
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from models import Message
import json
from typing import Dict, List
from chat_utils import send_message, get_text_message_body, get_text_message_body_template

#Loading the environment variables
load_dotenv(override=True)

app = FastAPI()

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

messages_dict: Dict[str, List[Dict[str, str]]] = {}

def update_message_log(message: str, phone_number: str, role: str) -> Dict[str, List[str]]:
    system_message = "You are a helpful assistant that responds politely to all the user messages."
    system_message += "If you do not know the answer to something, just say so."
    if phone_number not in messages_dict:
        messages_dict[phone_number] = [{"role": "system", "content": system_message}]
    messages_dict[phone_number].append({"role": role, "content": message})
    return messages_dict

def check_vacancies(location: str) -> str:
    vacancies: int = 0
    if(location == "karapakkam"):
        vacancies = 2
    elif location == "thuraipakkam":
        vacancies = 0
    if vacancies != 0:
        return f"We currently have {vacancies} vacancies at {location} location"
    else:
        return f"We currently have no available rooms at {location} location"
    

# TODO - Make code such that the response is generated based on the message recipient number. IE: Response template and generic message should be specific to each business owner
# TODO - Create map for the templates owned by each business owner. Template name should be sent as a parameter for body to be generated.

def generate_message_response(message_log: List[str]) -> str:
    if(len(message_log) > 2):
        print(message_log[-3])
    logger.info("User message logs")
    logger.info(message_log)
    if(message_log[-1]["content"].lower() == "Hi".lower()):
        return "TEMPLATE"
    elif(message_log[-1]["content"].lower() == "Check Vacancies".lower()):
        return "Please enter the location name: Karapakkam, Sholinganallur_1, Sholinganallur_1, Thuraipakkam, Tharamani"
    elif(message_log[-3]["content"].lower() == "Check Vacancies".lower()):
        logger.info("Checking Vacancies")
        return check_vacancies(message_log[-1]["content"].lower())
    else:
        return "Thank you for sending a message. We will get back to you shortly."

async def send_whatsapp_message(body, response: str):
    value = body["entry"][0]["changes"][0]["value"]
    from_number = value["messages"][0]["from"]
    recipient = from_number
    if(response == "TEMPLATE"):
        await send_message(get_text_message_body_template(recipient))
    else:
        await send_message(get_text_message_body(recipient, response))

async def handle_whatsapp_message(body):
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    if message["type"] == "text":
        message_body = message["text"]["body"]
    
    if message["type"] == "button":
        message_body = message["button"]["text"]

    # TODO: Implement functionality to handle other message types

    message_log = update_message_log(message_body, message["from"], "user")
    response = generate_message_response(message_log[message["from"]])
    await send_whatsapp_message(body, response)
    update_message_log(response, message["from"], "assistant")


@app.get("/")
async def read_root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to the production-ready FastAPI app!"
    }

@app.get("/webhook")
def register_webhook(
        hub_mode: str = Query(..., alias="hub.mode"), 
        hub_challenge: int = Query(..., alias="hub.challenge"), 
        hub_verify_token: str = Query(..., alias="hub.verify_token")
    ):

    print(hub_mode)

    if( hub_mode == 'subscribe' and hub_verify_token == os.getenv("WA_WEBHOOK_CHALLENGE_TOKEN")):
        return hub_challenge
    else:
        raise HTTPException(status_code=400, detail="Authentication unsuccessful")

@app.post("/webhook")
async def process_webhook(request: Request):
    body = await request.body()
    body_obj = json.loads(body.decode('utf-8'))
    logger.info("Webhook request Received")
    logger.info(json.dumps(body_obj))
    try:
        # info on WhatsApp text message payload:
        # https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples#text-messages
        if body_obj.get("object"):
            if (
                body_obj.get("entry")
                and body_obj["entry"][0].get("changes")
                and body_obj["entry"][0]["changes"][0].get("value")
                and body_obj["entry"][0]["changes"][0]["value"].get("messages")
                and body_obj["entry"][0]["changes"][0]["value"]["messages"][0]
            ):
                logger.info("handling message")
                await handle_whatsapp_message(body_obj)
        else:
            raise HTTPException(status_code=404, detail="Not a Whatsapp API event")

    except Exception as e:
        logger.error(f"Unknown Error: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred")
    
@app.get("/send-test-message")
async def send_test_message():
    try:
        await send_message(get_text_message_body("916380104477", "Heyy There!"))
    except HTTPException:
        raise HTTPException(status_code=500, detail="An internal server error occurred")