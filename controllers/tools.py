import os
import json
import requests
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import Tool
from langchain_community.utilities.alpha_vantage import AlphaVantageAPIWrapper
from langchain_apify import ApifyActorsTool
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from email.mime.multipart import MIMEMultipart
from litellm import completion
import smtplib
from email.mime.text import MIMEText

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
        response = apify_tool.invoke(
            {"run_input": {"query": query, "maxResults": max_results}}
        )

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

        return {"symbol": symbol, "price": stock_price}
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


def get_mail_body_subject_from_query(query):
    prompt = f"""
    Given the query: "{query}", analyze the content and extract the necessary information to send an email. The information needed includes the recipient's email address, the subject of the email, and the body content of the email. 
    Based on the analysis, return a dictionary in Python format where the keys are 'recipient', 'subject', and 'body', and the values are the corresponding pieces of information extracted from the query. 
    For example, if the query was about sending an email to notify someone of an upcoming event, the output should look like this:
    {{
        "recipient": "example@example.com",
        "subject": "Upcoming Event Notification",
        "body": "Dear [Name], we would like to remind you of the upcoming event happening next week. We look forward to seeing you there."
    }}
    Now, based on the provided query, return the structured information as described.
    Return a valid directly parsable json, dont return in it within a code snippet or add any kind of explanation!!
    """
    model_name = "gpt-4o-mini"
    response = completion(
        model=model_name,
        messages=[{"content": prompt, "role": "user"}],
        max_tokens=1000,
        temperature=0.2,
    )
    mail_body_subject = response.choices[0].message.content.strip()
    print(mail_body_subject)
    return mail_body_subject


def send_email_with_gmail(email_details):
    """.env should include GMAIL_MAIL and GMAIL_APP_PASSWORD to work correctly"""
    try:
        sender_email = os.getenv("GMAIL_MAIL")
        app_password = os.getenv("GMAIL_APP_PASSWORD")
        recipient_email = email_details["recipient"]
        subject = email_details["subject"]
        body = email_details["body"]
        # Create MIME message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Create server object with SSL option
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, app_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        return "Email sent successfully."
    except Exception as e:
        return f"Email was not sent successfully, error: {e}"


def send_email_tool(query):
    """Sends an email based on the single query string"""
    email_details = get_mail_body_subject_from_query(query)
    if isinstance(email_details, str):
        email_details = json.loads(email_details)  # Ensure it's a dictionary
    print("EMAIL DETAILS")
    print(email_details)
    result = send_email_with_gmail(email_details)
    return result


def generate_calendly_invitation_link(query):
    """Generate a calendly invitation link based on the single query string"""
    event_type_uuid = os.getenv("CALENDLY_EVENT_UUID")
    api_key = os.getenv("CALENDLY_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    url = "https://api.calendly.com/scheduling_links"
    payload = {
        "max_event_count": 1,
        "owner": f"https://api.calendly.com/event_types/{event_type_uuid}",
        "owner_type": "EventType",
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        data = response.json()
        return f"url: {data['resource']['booking_url']}"
    else:
        return "Failed to create Calendly link: "


send_calendly_tool = Tool(
    name="SendCalendlyInvitation",
    func=generate_calendly_invitation_link,
    description="""Useful for when you need to create invite for a personal meeting in Sleep Heaven shop. 
            Sends a calendly invitation based on the query input.""",
)

email_tool = Tool(
    name="SendEmail",
    func=send_email_tool,
    description="Sends an email based on the query input. The query should specify the recipient, subject, and body of the email.",
)

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
