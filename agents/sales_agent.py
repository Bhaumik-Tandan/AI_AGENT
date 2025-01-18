from core.agent import Agent
from core.knowledge_base import KnowledgeBase
from core.action_registry import ActionRegistry
from core.prompt_engine import PromptEngine

def setup_sales_agent() -> Agent:
    # Initialize knowledge base
    knowledge = KnowledgeBase()
    
    # Initialize action registry
    actions = ActionRegistry()
    
    # Register common sales actions
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
    
    # Initialize prompt engine
    prompt_engine = PromptEngine()
    
    # Register system prompt for sales agent
    prompt_engine.register_system_prompt(
        "sales",
        """You are an AI sales assistant. Your goals are to:
        1. Collect relevant information about potential customers
        2. Answer questions about our product
        3. Schedule demos when appropriate
        4. Follow up with leads
        Always be professional and helpful."""
    )
    
    # Create and return the agent
    return Agent(
        knowledge=knowledge,
        action_registry=actions,
        prompt_engine=prompt_engine,
        agent_type="sales"
    )