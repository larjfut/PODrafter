import json
import logging
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from ..middleware.auth import verify_api_key
from ..services.openai_client import client
from ..utils.sanitization import sanitize_string, DISALLOWED_PATTERNS
from ..utils.validation import MAX_REQUEST_SIZE, MAX_FIELD_LENGTH

logger = logging.getLogger(__name__)


class Message(BaseModel):
  role: Literal["user", "assistant", "system"]
  content: str


class ChatRequest(BaseModel):
  messages: list[Message]


class Upsert(BaseModel):
  source_msg_id: str
  confidence: float
  county: str | None = None
  case_no: str | None = None
  hearing_date: str | None = None
  petitioner_full_name: str | None = None
  petitioner_address: str | None = None
  petitioner_phone: str | None = None
  petitioner_email: str | None = None
  respondent_full_name: str | None = None
  firearm_surrender: bool | None = None

  @field_validator("*", mode="before")
  @classmethod
  def sanitize_fields(cls, v):
    if isinstance(v, str):
      return sanitize_string(v)
    return v

  @field_validator("confidence")
  @classmethod
  def validate_confidence(cls, v: float) -> float:
    if v < 0 or v > 1:
      raise ValueError("confidence must be between 0 and 1")
    return v

  model_config = {"ser_json_exclude_none": True}


class ChatResponse(BaseModel):
  messages: list[Message]
  upserts: list[Upsert]


SYSTEM_PROMPT = """You are a trauma-informed legal assistant helping create protective order petitions in Texas. You are compass
ionate, patient, and professional.

CORE RESPONSIBILITIES:
1. Ask trauma-informed questions to gather required petition information
2. ALWAYS call set_petition_data when you learn ANY petition details
3. Guide users through required fields: county, petitioner_full_name, respondent_full_name
4. Provide emotional support and brief legal context
5. Maintain a caring, non-judgmental tone throughout

TRAUMA-INFORMED APPROACH:
- Let them share at their own pace
- Acknowledge their courage: "Taking this step shows real strength"
- Validate their feelings: "I understand this is difficult"
- Be patient and never rush them
- Explain why you need certain information

INFORMATION TO COLLECT:
- county (required): Harris, Dallas, Travis, or General for other Texas counties
- petitioner_full_name (required): Their full legal name as on ID
- respondent_full_name (required): Full name of person they need protection from
- petitioner_address (optional): Safe mailing address
- petitioner_phone (optional): Contact number
- petitioner_email (optional): Email for court notifications
- firearm_surrender (optional): Whether respondent should surrender firearms

FUNCTION CALLING RULES:
- Call set_petition_data IMMEDIATELY when learning any information
- Even partial info (like first name only) should be saved, then updated later
- Always acknowledge what you've recorded: "I've noted that information"
- Update fields when you get more complete information

CONVERSATION FLOW:
1. Welcome warmly and ask about their safety
2. Ask which county they want to file in
3. Ask for their name when ready
4. Gently ask about the other person's name
5. Collect additional details as they share their story
6. Provide encouragement throughout

Remember: You're helping someone take a critical step toward safety. Be gentle, patient, and supportive."""


TOOLS = [
  {
    "type": "function",
    "function": {
      "name": "set_petition_data",
      "description": "Upsert petition fields extracted from conversation",
      "parameters": {
        "type": "object",
        "properties": {
          "county": {
            "type": "string",
            "enum": ["Harris", "Dallas", "Travis", "General"],
          },
          "case_no": {"type": "string"},
          "hearing_date": {"type": "string"},
          "petitioner_full_name": {"type": "string"},
          "petitioner_address": {"type": "string"},
          "petitioner_phone": {"type": "string"},
          "petitioner_email": {"type": "string"},
          "respondent_full_name": {"type": "string"},
          "firearm_surrender": {"type": "boolean"},
          "source_msg_id": {"type": "string"},
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1,
          },
        },
        "required": ["source_msg_id", "confidence"],
        "additionalProperties": False,
      },
    },
  }
]

router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(chat_request: ChatRequest, request: Request) -> ChatResponse:
  verify_api_key(request)

  payload = chat_request.model_dump()
  if len(json.dumps(payload).encode("utf-8")) > MAX_REQUEST_SIZE:
    raise HTTPException(status_code=413, detail="Request too large")

  for msg in chat_request.messages:
    if len(msg.content) > MAX_FIELD_LENGTH:
      raise HTTPException(status_code=413, detail="Field too large")
    for pattern in DISALLOWED_PATTERNS:
      if pattern.search(msg.content):
        raise HTTPException(status_code=400, detail="Invalid content")

  user_messages = [
    {"role": msg.role, "content": sanitize_string(msg.content)}
    for msg in chat_request.messages
  ]
  openai_messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    *user_messages,
  ]

  try:
    response = await client.chat.completions.create(
      model="gpt-4o",
      messages=openai_messages,
      temperature=0.7,
      tools=TOOLS,
      tool_choice="auto",
    )
    msg = response.choices[0].message
    upserts: list[Upsert] = []
    for call in getattr(msg, "tool_calls", []) or []:
      name = getattr(getattr(call, "function", None), "name", "")
      if name not in {"set_petition_data", "upsert_petition"}:
        continue
      arguments = getattr(getattr(call, "function", None), "arguments", "{}") or "{}"
      try:
        raw = json.loads(arguments)
      except json.JSONDecodeError:
        logger.debug("invalid JSON in tool call arguments", extra={"function": name})
        continue
      logger.info("extracted petition data", extra={"fields": list(raw.keys())})
      try:
        upserts.append(Upsert(**raw))
      except Exception as exc:
        logger.debug(
          "invalid upsert payload",
          extra={"error": str(exc), "fields": list(raw.keys())},
        )
    assistant_message = {"role": "assistant", "content": sanitize_string(msg.content or "")}
    full_messages = [Message(**m) for m in user_messages + [assistant_message]]
    result = ChatResponse(messages=full_messages, upserts=upserts)
    return JSONResponse(content=result.model_dump(exclude_none=True))
  except HTTPException:
    raise
  except Exception as e:
    logger.exception("chat endpoint failed", exc_info=e)
    raise HTTPException(status_code=500, detail="Internal server error") from e
