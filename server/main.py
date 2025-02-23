import os
from dotenv import load_dotenv
import logging
from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
import json

#Loading the environment variables
load_dotenv(override=True)

# whatsapp_access_token: str = os.getenv("WA_ACCESS_TOKEN")
# print(whatsapp_access_token)

app = FastAPI()


# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def read_root():
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to the production-ready FastAPI app!"
    }

@app.get("/webhook")
async def register_webhook(
        hub_mode: str = Query(..., alias="hub.mode"), 
        hub_challenge: str = Query(..., alias="hub.challenge"), 
        hub_verify_token: str = Query(..., alias="hub.verify_token")
    ):

    print(hub_mode)

    if( hub_mode == 'subscribe' and hub_verify_token == os.getenv("WA_WEBHOOK_CHALLENGE_TOKEN")):
        return hub_challenge
    else:
        raise HTTPException(status_code=400, detail="Authentication unsuccessful")
