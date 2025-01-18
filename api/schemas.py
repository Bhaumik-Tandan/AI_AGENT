from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime

class ConversationStart(BaseModel):
    user_id: Optional[str] = None
    agent_type: str = "sales"

class MessageRequest(BaseModel):
    session_id: str
    message: str
    metadata: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    session_id: str
    response: Dict[str, Any]
    current_state: str
    collected_info: Dict[str, Any]
    required_info: List[str]
    timestamp: datetime = Field(default_factory=datetime.now)

class KnowledgeAddRequest(BaseModel):
    category: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ConversationEnd(BaseModel):
    session_id: str