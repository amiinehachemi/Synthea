# AI-AGENT
# Synthea

# Advanced AI Chatbot with Tool Integration

This project is an advanced AI chatbot that integrates multiple tools for enhanced functionality, including web search, stock price checking, web scraping, and image generation. The chatbot is built using Python (Flask for the backend) and React for the frontend, with LangChain for AI tool integration.

## Features

- **Web Search**: Perform web searches using the Tavily API.
- **Stock Price Checking**: Fetch real-time stock prices using Alpha Vantage.
- **Web Scraping**: Extract structured data from web pages using Apify's RAG Web Browser.
- **Image Generation**: Generate images based on textual prompts using DALL·E.
- **Session Management**: Maintains user sessions and enforces rate limits.
- **Interactive UI**: A React-based frontend for seamless user interaction.

## Tools Integrated

1. **Tavily Search API**: For real-time web search results.
2. **Alpha Vantage API**: For stock market data.
3. **Apify Actors**: For web scraping tasks.
4. **DALL·E API**: For generating images from text prompts.

## Prerequisites

- Python 3.8+
- Node.js (for the frontend)
- API keys for:
  - Tavily
  - Alpha Vantage
  - Apify
  - OpenAI (for DALL·E)

## Setup Instructions

### Backend (Flask)

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-folder>

Set up a virtual environment:

bash
Copy
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
Copy
pip install -r requirements.txt
Set up environment variables:
Create a .env file in the root directory and add your API keys:

env
Copy
TAVILY_API_KEY=your_tavily_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
APIFY_API_KEY=your_apify_api_key
OPENAI_API_KEY=your_openai_api_key
Run the Flask server:

bash
Copy
python app.py
The backend will run on http://localhost:5000.

Frontend (React)
Navigate to the frontend directory:

bash
Copy
cd frontend
Install dependencies:

bash
Copy
npm install
Run the React app:

bash
Copy
npm start
The frontend will run on http://localhost:5173.

Usage
Open the React app in your browser (http://localhost:5173).

Interact with the chatbot by typing messages in the input box.

The chatbot will use the appropriate tool based on your query and provide a response.

Example Queries
Web Search: "What is the latest news on AI?"

Stock Price: "What is the current price of AAPL?"

Web Scraping: "Scrape the latest articles from TechCrunch."

Image Generation: "Generate an image of a futuristic city."

API Endpoints
Health Check: GET /health

Rate Limiting
The chatbot enforces a rate limit of 10 requests per minute per session. If the limit is exceeded, the user will receive an error message.

Session Management
Sessions are automatically cleaned up after 5 minutes of inactivity. A background thread runs every hour to remove inactive sessions.

Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
