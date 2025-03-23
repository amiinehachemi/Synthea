"use client"

import { useState, useEffect, useRef } from "react"
import { MessageSquare, Send, Paperclip, Mic } from "lucide-react"
import "./AIChatPro.css"
import avatar from "./assets/avatar.png";
import axios from "axios";
import get from "lodash/get";

const api = axios.create({
  baseURL: process.env.NODE_ENV === "production" ? "https://your-prod-url.com" : "http://localhost:5000",
});


export default function AIChatPro() {
  const [sessionKey, setSessionKey] = useState(null);
  const [inputValue, setInputValue] = useState("")
  const [messages, setMessages] = useState([])
  const [activeTool, setactiveTool] = useState()
  const [loading, setLoading] = useState(false); // Track API request state

  const tools = [
    {
      name: 'Send Email',
      description: 'Allows AI Agent to send emails directly, enabling seamless communication and notifications within your workflow.',
      metadata: 'SendEmail',
    },
    {
      name: 'Calendly Invitation',
      description: 'Easily schedule meetings by sending Calendly invitations, streamlining appointment booking and time management using AI Agent.',
      metadata: 'SendCalendlyInvitation',
    },
    {
      name: 'DALL·E 3',
      description: 'DALL·E 3 understands significantly more nuance and detail than our previous systems, allowing you to easily translate your ideas into exceptionally accurate images.',
      metadata: 'image_generation',
    },
    {
      name: 'Tavily',
      description: 'Tavily Search API is a specialized search engine designed for Large Language Models. It provides real-time, accurate, and unbiased information, enabling AI applications to retrieve and process data efficiently.',
      metadata: 'web_search',
    },
    {
      name: 'Apify Actors',
      description: 'ApifyActorsTool lets you call Apify Actors to provide your CrewAI workflows with web scraping, crawling, data extraction, and web automation capabilities.',
      metadata: 'apify_web_scraper',
    },
    {
      name: 'Alpha Vantage',
      description: 'Alpha Vantage provides realtime and historical financial market data, From traditional asset classes (e.g., stocks, ETFs, mutual funds) to economic indicators, from foreign exchange rates to commodities, from fundamental data to technical indicators.',
      metadata: 'stock_price_checker',
    },
  ]
  /**
   * scrollbar to automatically scroll 
   */
  const scrollToActiveCard = () => {
    const activeCard = document.querySelector('.tool-card.active');
    if (activeCard) {
      activeCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }

  // Run the function whenever the active class is added
  const observer = new MutationObserver(scrollToActiveCard);
  observer.observe(document.body, { subtree: true, attributes: true, attributeFilter: ['class'] });


  const handleSendMessage = async () => {
    if (!inputValue.trim() || loading) return;
    setLoading(true);
    const userMessage = { id: messages.length + 1, content: inputValue, sender: "user" };
    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    try {
      const response = await api.post("/query", {
        query: inputValue,
        session_key: sessionKey,
      });
      console.log('response', response)
      const aiMessage = {
        id: userMessage.id + 1,
        content: get(response, "data.reply.answer", "No response received."),
        imageUrl: get(response, "data.reply.imageUrl", null),
        tool: get(response, "data.reply.tool", null),
        sender: "ai",
      };
      setMessages((prev) => [...prev, aiMessage]);
      setactiveTool(get(response, "data.reply.tool", ''))
    } catch (error) {
      console.error("Error fetching AI response:", error);
    } finally {
      setLoading(false)
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey && !loading) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  useEffect(() => {
    const loadFingerprint = async () => {
      try {
        const FingerprintJS = await import("https://openfpcdn.io/fingerprintjs/v4");
        const fp = await FingerprintJS.load();
        const result = await fp.get();
        setSessionKey(result.visitorId);

      } catch (error) {
        console.error("FingerprintJS failed:", error);
      }
    };
    loadFingerprint();
  }, []);

  const welcomeMessage = async () => {
    try {
      // Check if the message has already been sent in this session
      if (sessionStorage.getItem("welcomeMessageSent")) return;
  
      const response = await api.post("/query", {
        query: "Hello",
        session_key: sessionKey,
      });
  
      const aiMessage = {
        content: get(response, "data.reply.answer", "No response received."),
        sender: "ai",
      };
  
      setMessages((prev) => [...prev, aiMessage]);
  
      // Mark as sent for this session only (persists after refresh, resets on tab close)
      sessionStorage.setItem("welcomeMessageSent", "true");
    } catch (error) {
      console.error("welcomeMessage failed:", error);
    }
  };
  const hasRun = useRef(false);

  useEffect(() => {
    if (!hasRun.current) {
      hasRun.current = true; 
      welcomeMessage();
    }
  }, []);

  return (
    <div className="chat-container">
      <div className="chat-box">
        {/* Header */}
        <div className="chat-header">
          <div className="chat-title">
            <MessageSquare size={20} />
            <h1>Synthea</h1>
          </div>
          <button className="voice-button">Switch to Voice</button>
        </div>

        {/* Main content */}
        <div className="chat-content">
          {/* Chat area */}
          <div className="chat-messages">
            <div className="messages-list">
              {messages.map((message) => (
                <div key={message.id} className={`message ${message.sender}`}>
                  {message.sender === "user" ? (
                    <div className="user-message">
                      <div className="message-content">
                        <p className="message-content-user">{message.content}</p>
                      </div>
                      <div className="user-avatar">
                        <img src={avatar} alt="User Avatar" className="avatar-img" />
                      </div>
                    </div>
                  ) : (
                    <div className="message-content-reply">
                      <p className="message-content-ai">{message.content}</p>
                      {message.imageUrl ? (
                        <img src={message.imageUrl} alt="AI response image" className="message-image" />
                      ) : (
                        <p></p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Right sidebar */}
          <div className="chat-sidebar">
            <h2 className="sidebar-title">Agent Tool Suggestions</h2>
            <p className="sidebar-info">An animation effect will be displayed if the AI selects a tool.</p>
            <div className="tool-cards">
              {tools.map((tool, index) => (
                <div
                  key={index}
                  className={`tool-card ${tool.metadata === activeTool ? "active" : ""}`}
                >
                  <h3>{tool.name}</h3>
                  <p>{tool.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Message input */}
        <div className="chat-input">
          <div className="input-container">
            <input
              type="text"
              className="message-input"
              placeholder="Type a message..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <div className="action-buttons">
              <button className="action-button" onClick={handleSendMessage}>
                <Send color="#000000" strokeWidth={2.3} />
              </button>
              {/* <button className="action-button">
                <Paperclip color="#000000" strokeWidth={2.3} />
              </button> */}
              <button className="action-button">
                <Mic color="#000000" strokeWidth={2.3} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

