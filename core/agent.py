from typing import Dict, Any, List
import logging
from core.context import ConversationContext
from core.knowledge_base import KnowledgeBase
from core.action_registry import ActionRegistry
from core.prompt_engine import PromptEngine
from core.response_parser import JSONResponseParser
from openai import OpenAI

client = OpenAI()
from config.settings import MODEL_NAME, MAX_TOKENS, TEMPERATURE

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self,
                 knowledge: KnowledgeBase,
                 action_registry: ActionRegistry,
                 prompt_engine: PromptEngine,
                 agent_type: str = "sales"):
        self.knowledge = knowledge
        self.action_registry = action_registry
        self.prompt_engine = prompt_engine
        self.agent_type = agent_type
        self.response_parser = JSONResponseParser()

    def process_message(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        try:
            # 1. Retrieve relevant knowledge
            relevant_info = self.knowledge.query_knowledge(message, category=self.agent_type)

            # 2. Build dynamic prompt
            prompt = self.prompt_engine.build_prompt(
                self.agent_type,
                message,
                context,
                relevant_info
            )

            # 3. Get AI response
            response = self._get_ai_response(prompt)

            # 4. Parse response
            parsed_response = self.response_parser.parse(response)
            
            # 5. Execute actions and update context
            self._handle_actions(parsed_response, context)

            # 6. Update conversation context
            context.add_message("user", message)
            context.add_message("assistant", parsed_response["response"])
           
            context.current_state = parsed_response.get("next_state", context.current_state)

            # 7. Update required information
            context.required_info = parsed_response.get("required_information", [])
            
            return parsed_response

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            raise

    def _get_ai_response(self, prompt: str) -> str:
        try:
            response = client.chat.completions.create(model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are an AI assistant following strict response format."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting AI response: {str(e)}")
            raise

    def _handle_actions(self, parsed_response: Dict[str, Any], context: ConversationContext):
        for action in parsed_response.get("actions", []):
            try:
                action_name = action.get("name")
                parameters = action.get("parameters", {})

                if self.action_registry.has_action(action_name):
                    self.action_registry.execute(action_name, **parameters)
                else:
                    logger.warning(f"Unknown action requested: {action_name}")

            except Exception as e:
                logger.error(f"Error executing action {action.get('name')}: {str(e)}")