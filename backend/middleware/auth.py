import os
from fastapi import HTTPException, Request

CHAT_API_KEY = os.getenv("CHAT_API_KEY") or os.getenv("PUBLIC_CHAT_API_KEY")


def verify_api_key(request: Request) -> None:
  provided = request.headers.get("X-API-Key")
  if CHAT_API_KEY is None:
    raise HTTPException(status_code=500, detail="Server misconfiguration")
  if not provided or provided != CHAT_API_KEY:
    raise HTTPException(status_code=401, detail="Unauthorized")


def get_client_ip(request: Request) -> str:
  if request.client and request.client.host:
    return request.client.host
  return "anon"
