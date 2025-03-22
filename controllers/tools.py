from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import Tool
from langchain_community.utilities.alpha_vantage import AlphaVantageAPIWrapper
from langchain_apify import ApifyActorsTool
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper

from dotenv import load_dotenv
load_dotenv()

# Initialize API clients
alpha_vantage = AlphaVantageAPIWrapper()
search = TavilySearchResults(max_results=2)
apify_tool = ApifyActorsTool("apify/rag-web-browser")



def scrape_web_with_apify(query: str, max_results: int = 2):
    """Scrapes web pages using Apify's RAG Web Browser and extracts relevant data."""
    try:
        apify_tool = ApifyActorsTool("apify/rag-web-browser")
        response = apify_tool.invoke({"run_input": {"query": query, "maxResults": max_results}})

        if not response:
            return {"error": f"No data found for '{query}'"}

        return {"query": query, "scraped_data": response}
    except Exception as e:
        return {"error": str(e)}

    
def get_stock_price(symbol: str):
    """Fetches the latest stock price for a given symbol using Alpha Vantage."""
    try:
        data = alpha_vantage._get_quote_endpoint(symbol)
        stock_info = data.get("Global Quote", {})

        if not stock_info:
            return {"error": f"No stock data found for {symbol}"}

        # Extract stock price safely
        stock_price = stock_info.get("05. price", "N/A")

        return {
            "symbol": symbol,
            "price": stock_price
        }
    except Exception as e:
        return {"error": str(e)}


def search_web(query: str):
    """Performs a web search using the Tavily API and returns top results."""
    try:
        results = search.run(query) 
        return {"query": query, "results": results}
    except Exception as e:
        return {"error": str(e)}


def generate_image(prompt: str):
    """Generates an image based on the provided textual prompt using DALL·E."""
    try:
        dalle = DallEAPIWrapper()
        image_url = dalle.run(prompt)
        return {"prompt": prompt, "image_url": image_url}
    except Exception as e:
        return {"error": str(e)}
    
image_generation_tool = Tool(
    name="image_generation",
    func=generate_image,
    description="Generates an image based on the provided textual prompt using DALL·E.",
)
    
search_tool = Tool(
    name="web_search",
    func=search_web,
    description="Searches the web for information on a given topic or question.",
)

apify_web_scraper_tool = Tool(
    name="apify_web_scraper",
    func=scrape_web_with_apify,
    description="Extracts structured data from web pages using Apify's RAG Web Browser. Ideal for web scraping tasks like retrieving product details, news articles, or structured data from websites.",
)

alpha_vantage_tool = Tool(
    name="stock_price_checker",
    func=get_stock_price,
    description="Gets the latest stock price for a given stock symbol (e.g., 'AAPL', 'IBM').",
)

    