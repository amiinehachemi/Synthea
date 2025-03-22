import os
from flask import Flask, jsonify, request
from flask_cors import CORS  # type: ignore
from controllers.agent import AgentHandler
import warnings
import asyncio
warnings.filterwarnings("ignore", category=UserWarning, module="langsmith.client")

# Set environment variable (default to 'develop' if not set)
environment = os.getenv('ENV', 'develop')
port = int(os.getenv('PORT', 5000))  # Convert to intexit

app = Flask(__name__)

# Enable CORS for all domains and methods
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})


print(f"Starting version: 1.00 in {environment} environment on port {port}")

@app.route('/health', methods=['GET'])
def get_health_check():
    """Function printing service health."""
    return jsonify({"status": "healthy"}), 200


@app.route('/query', methods=['POST'])
def handle_query():
    """Handles AI chatbot queries and manages session keys."""
    data = request.json
    query = data.get("query", "").strip()
    session_key = data.get("session_key")

    if not query:
        return jsonify({"error": "Query is required"}), 400

    # Simulated AI response (Replace this with actual AI processing)
    agent_handler = AgentHandler()
    response = agent_handler.agent_instance(query, session_key)

    return jsonify({
        "reply": response,
        "session_key": session_key  # Return session key to maintain state
    })


# # Interactive Chat in the Command Line
# def chat_loop():
#     print("AI Chat is running! Type your message and press Enter. Type 'exit' to stop.")
#     session_id = "default_session"
    
#     while True:
#         query = input("\nYou: ")  # Get user input
#         if query.lower() in ["exit", "quit"]:
#             print("Exiting chat. Goodbye!")
#             break
        
#         response = agent_instance(query, session_id)
#         print("AI:", response)
        
        
if __name__ == "__main__":
    is_debug = environment.lower() != 'production'
    app.run(host="0.0.0.0", port=port, debug=is_debug)
