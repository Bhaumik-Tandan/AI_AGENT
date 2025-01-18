from flask import Blueprint, request, jsonify
from core.agent import Agent
from core.context import ConversationContext
from agents.sales_agent import setup_sales_agent
from typing import Dict
import uuid
import logging

logger = logging.getLogger(__name__)

# Store active conversations
active_conversations: Dict[str, ConversationContext] = {}

def setup_routes(app):
    api = Blueprint('api', __name__)

    @api.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "version": "1.0.0"})

    @api.route('/conversation/start', methods=['POST'])
    def start_conversation():
        try:
            data = request.json
            user_id = data.get('user_id', str(uuid.uuid4()))
            agent_type = data.get('agent_type', 'sales')  # Default to sales agent
            
            # Create new conversation context
            session_id = str(uuid.uuid4())
            context = ConversationContext(
                user_id=user_id,
                session_id=session_id,
                agent_id=agent_type
            )
            
            active_conversations[session_id] = context
            
            return jsonify({
                "session_id": session_id,
                "user_id": user_id,
                "message": "Conversation started successfully"
            })
        except Exception as e:
            logger.error(f"Error starting conversation: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @api.route('/conversation/message', methods=['POST'])
    def send_message():
        try:
            data = request.json
            session_id = data.get('session_id')
            message = data.get('message')
            
            if not session_id or not message:
                return jsonify({"error": "Missing session_id or message"}), 400
            
            context = active_conversations.get(session_id)
            if not context:
                return jsonify({"error": "Invalid session_id"}), 404
            
            # Get appropriate agent based on context
            agent = setup_sales_agent()  # For now, always using sales agent
            
            # Process message
            response = agent.process_message(message, context)
            print("in send_message", response)
            
            return jsonify({
                "session_id": session_id,
                "response": response,
                "current_state": context.current_state,
                "collected_info": context.collected_info,
                "required_info": context.required_info
            })
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @api.route('/conversation/end', methods=['POST'])
    def end_conversation():
        try:
            session_id = request.json.get('session_id')
            if not session_id:
                return jsonify({"error": "Missing session_id"}), 400
                
            if session_id in active_conversations:
                del active_conversations[session_id]
                
            return jsonify({
                "message": "Conversation ended successfully",
                "session_id": session_id
            })
        except Exception as e:
            logger.error(f"Error ending conversation: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @api.route('/knowledge', methods=['POST'])
    def add_knowledge():
        try:
            data = request.json
            category = data.get('category')
            content = data.get('content')
            metadata = data.get('metadata', {})
            
            if not category or not content:
                return jsonify({"error": "Missing category or content"}), 400
            
            agent = setup_sales_agent()
            knowledge_id = agent.knowledge.add_knowledge(category, content, metadata)
            
            return jsonify({
                "message": "Knowledge added successfully",
                "knowledge_id": knowledge_id
            })
        except Exception as e:
            logger.error(f"Error adding knowledge: {str(e)}")
            return jsonify({"error": str(e)}), 500

    app.register_blueprint(api, url_prefix='/api/v1')