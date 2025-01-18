from typing import Dict, List, Any
import json
from dataclasses import dataclass
from core.context import ConversationContext

@dataclass
class PromptTemplate:
    template: str
    required_variables: List[str]
    
    def format(self, **kwargs) -> str:
        missing = [var for var in self.required_variables if var not in kwargs]
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
        return self.template.format(**kwargs)

class PromptEngine:
    def __init__(self):
        self.system_prompts = {}
        self.state_prompts = {}

    def register_system_prompt(self, agent_type: str, prompt: str):
        self.system_prompts[agent_type] = prompt

    def register_state_prompt(self, agent_type: str, state: str, prompt: PromptTemplate):
        if agent_type not in self.state_prompts:
            self.state_prompts[agent_type] = {}
        self.state_prompts[agent_type][state] = prompt

    def build_prompt(self, 
                    agent_type: str, 
                    message: str, 
                    context: ConversationContext, 
                    relevant_knowledge: List[Dict[str, Any]]) -> str:
        system_prompt = self.system_prompts.get(agent_type, "")
        state_prompt = self.state_prompts.get(agent_type, {}).get(context.current_state)

        # Build the dynamic prompt structure
        prompt_structure = {
            "system": system_prompt,
            "context": {
                "current_state": context.current_state,
                "collected_information": context.collected_info,
                "missing_information": context.get_missing_info(),
                "conversation_history": context.conversation_history[-5:]  # Last 5 messages
            },
            "knowledge": relevant_knowledge,
            "user_message": message,
            "response_format": {
                "response": "string - your response to the user",
                "actions": "array of action objects with name and parameters",
                "required_information": "array of required information fields",
                "next_state": "string - the next conversation state",
                "confidence": "float - confidence score for the response"
            }
        }

        if state_prompt:
            try:
                state_specific_content = state_prompt.format(
                    collected_info=json.dumps(context.collected_info),
                    missing_info=json.dumps(context.get_missing_info()),
                    current_state=context.current_state
                )
                prompt_structure["state_specific"] = state_specific_content
            except ValueError as e:
                prompt_structure["state_specific"] = str(e)

        return json.dumps(prompt_structure, indent=2)