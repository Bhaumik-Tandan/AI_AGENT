from core.agent import Agent
from core.knowledge_base import KnowledgeBase
from core.action_registry import ActionRegistry
from core.prompt_engine import PromptEngine

def setup_sales_agent() -> Agent:
    knowledge = KnowledgeBase()
    
    actions = ActionRegistry()
    
    actions.register(
        "save_lead",
        lambda name, email: print(f"Lead saved: {name} ({email})"),
        "Save lead information to the database"
    )
    
    actions.register(
        "schedule_demo",
        lambda date, time: print(f"Demo scheduled for {date} at {time}"),
        "Schedule a product demonstration"
    )
    
    prompt_engine = PromptEngine()
    
    prompt_engine.register_system_prompt(
        "sales",
        """You are an AI sales assistant. Your goals are to:
        1. Collect relevant information about potential customers
        2. Answer questions about our product
        3. Schedule demos when appropriate
        4. Follow up with leads
        Always be professional and helpful."""
    )
    
    return Agent(
        knowledge=knowledge,
        action_registry=actions,
        prompt_engine=prompt_engine,
        agent_type="sales"
    )