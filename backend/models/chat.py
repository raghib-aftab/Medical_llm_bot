from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import zoneinfo

class Message(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")))

class Chat(BaseModel):
    title: str
    created_at: datetime = Field(default_factory=datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")))
    updated_at: datetime = Field(default_factory=datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")))
    messages: List[Message] = []

class ChatResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = []

class ChatListItem(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

class MessageRequest(BaseModel):
    content: str

class MessageResponse(BaseModel):
    role: str
    content: str
    timestamp: datetime
