from flask import Flask
from flask_cors import CORS
from api.routes import setup_routes
from config.settings import HOST, PORT
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    CORS(app)
    setup_routes(app)
    
    return app

if __name__ == "__main__":
    app = create_app()
    logger.info(f"Starting server on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=True)