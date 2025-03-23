import time
import asyncio
from collections import deque
import threading
import re
from dotenv import load_dotenv
from typing import Dict, Any, List
from langchain.chat_models import init_chat_model
from langchain.agents import create_tool_calling_agent
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.callbacks import BaseCallbackHandler
from controllers.tools import (
    alpha_vantage_tool,
    search_tool,
    apify_web_scraper_tool,
    image_generation_tool,
    email_tool,
    send_calendly_tool
)

load_dotenv()

store = {}
request_tracker = {}

# Cleanup (1 hour)
CLEANUP_INTERVAL = 3600


def run_cleanup_loop():
    """Background task for cleaning inactive sessions."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(cleanup_sessions())


async def cleanup_sessions():
    """Removes inactive sessions every hour."""
    while True:
        print("Clean sessions starts")
        await asyncio.sleep(CLEANUP_INTERVAL)
        now = time.time()
        for session in list(store.keys()):
            if (
                not request_tracker.get(session)
                or (now - request_tracker[session][-1]) > 300
            ):
                store.pop(session, None)  # Remove inactive sessions after 5 min
                request_tracker.pop(session, None)
                print("session key removed for", session)


# Start cleanup process in the background
threading.Thread(target=run_cleanup_loop, daemon=True).start()


class AgentHandler(BaseCallbackHandler):
    RATE_LIMIT = 10  # Max 10 requests per minute

    def __init__(self):
        self.tool_name = None
        self.model = init_chat_model("gpt-4o-mini", model_provider="openai")

    def is_rate_limited(self, session_key: str) -> bool:
        """Check if the session has exceeded the request limit."""
        now = time.time()
        if session_key not in request_tracker:
            print("store sessions key", session_key)
            request_tracker[session_key] = deque()

        timestamps = request_tracker[session_key]
        while timestamps and timestamps[0] < now - 60:  # Remove requests older than 60s
            print("delete sessions key", timestamps)
            timestamps.popleft()

        if len(timestamps) >= self.RATE_LIMIT:
            print("exceeded rate limits for ", timestamps)
            return True

        timestamps.append(now)
        return False
    def on_chain_end(self, outputs: Dict[str, Any], **kwargs) -> None:
        if outputs and isinstance(outputs, list) and hasattr(outputs[0], 'tool'):
            self.tool_name = outputs[0].tool  # Extract and assign the tool name
        print(f"Chain ended, tool_name: {self.tool_name}")
        if self.tool_name:
            global tool_name
            tool_name = self.tool_name
            
    def extract_image_data(self, output):
        """Extracts image URL and separates the answer text."""
        if not isinstance(output, dict) or "answer" not in output:
            return {"answer": "", "imageUrl": None}

        answer = output["answer"]
        match = re.search(r"!\[.*?\]\((.*?)\)", answer)

        return {
            "answer": re.sub(r"!\[.*?\]\(.*?\)", "", answer).strip(),
            "imageUrl": match.group(1) if match else None,
        }

    def agent_instance(self, query, session_key):
        try:
            print("sessions key for user is", session_key)
            if self.is_rate_limited(session_key):
                return {
                    "answer": "You have exceeded more than 10 requests per minute. Please try again later.",
                }

            tools = [
                alpha_vantage_tool,
                search_tool,
                image_generation_tool,
                apify_web_scraper_tool,
                email_tool,
                send_calendly_tool
            ]
            prompt = PromptTemplate.from_template(
                "You are an AI assistant and your name is Synthea. You are equipped with tools. "
                "Each tool serves a specific purpose. "
                "Your mission is to provide accurate and helpful responses to user queries by appropriately utilizing these tools when necessary. "
                "While doing so, maintain a fun yet professional tone to engage users effectively. "
                "Keep your responses in short length to retain the user's attention. Never produce lists, just answers."
                "Ensure that your responses are formatted for optimal readability, using bullet points, lists, or tables as appropriate. "
                "If a tool is required to answer the user's question, invoke it with the necessary parameters; otherwise, respond directly based on your knowledge. "
                "\n\nChat History:\n{chat_history}\n\nUser Query: {input}\n\n{agent_scratchpad}"
            )
            agent = create_tool_calling_agent(self.model, tools, prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            agent_with_chat_history = RunnableWithMessageHistory(
                agent_executor,
                self.get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
            )
            response = agent_with_chat_history.invoke(
                {"input": query},
                config={
                    "configurable": {"session_id": session_key},
                    "callbacks": [self],
                },
            )
            answer = response["output"]
            if self.tool_name == "image_generation":
                extracted_data = self.extract_image_data({"answer": answer})
                return {
                    "answer": extracted_data["answer"],
                    "imageUrl": extracted_data["imageUrl"],
                    "tool": self.tool_name,
                }
            return {"answer": answer, "tool": self.tool_name}
        except Exception as e:
            print("Error in agent_instance -->", e)

    def get_session_history(self, session_key: str) -> BaseChatMessageHistory:
        if session_key not in store:
            store[session_key] = ChatMessageHistory()
        return store[session_key]
