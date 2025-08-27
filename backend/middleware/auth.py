import os
from fastapi import HTTPException, Request

CHAT_API_KEY = os.getenv("CHAT_API_KEY")


def validate_api_key() -> None:
  if CHAT_API_KEY is None:
    raise RuntimeError("CHAT_API_KEY is not set")


def verify_api_key(request: Request) -> None:
  provided = request.headers.get("X-API-Key")
  if not provided or provided != CHAT_API_KEY:
    raise HTTPException(status_code=401, detail="Unauthorized")


def get_client_ip(request: Request) -> str:
  if request.client and request.client.host:
    return request.client.host
  return "anon"
