from dataclasses import dataclass, field
from typing import Dict, List, Any
from datetime import datetime

@dataclass
class ConversationContext:
    user_id: str
    session_id: str
    agent_id: str
    current_state: str = "initial"
    collected_info: Dict[str, Any] = field(default_factory=dict)
    required_info: List[str] = field(default_factory=list)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    last_interaction: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_message(self, role: str, content: str):
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.last_interaction = datetime.now()

    def update_collected_info(self, key: str, value: Any):
        self.collected_info[key] = value

    def is_required_info_complete(self) -> bool:
        return all(info in self.collected_info for info in self.required_info)

    def get_missing_info(self) -> List[str]:
        return [info for info in self.required_info if info not in self.collected_info]