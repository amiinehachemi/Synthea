"use client"

import { useState } from "react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { MessageSquare, Send, Paperclip, Mic } from "lucide-react"

export default function AIChatPro() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      content: "Hello! How can I assist you today?",
      sender: "ai",
    },
    {
      id: 2,
      content: "Can you recommend a tool for data visualization?",
      sender: "user",
    },
    {
      id: 3,
      content: "I recommend using Power BI for comprehensive data visualization needs.",
      sender: "ai",
    },
  ])

  const [inputValue, setInputValue] = useState("")

  const handleSendMessage = () => {
    if (inputValue.trim()) {
      setMessages([...messages, { id: messages.length + 1, content: inputValue, sender: "user" }])
      setInputValue("")
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="flex flex-col h-screen max-h-screen bg-gray-100">
      <div className="bg-white rounded-lg shadow-sm m-4 flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b flex justify-between items-center">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-5 w-5" />
            <h1 className="font-bold text-lg">AIChatPro</h1>
          </div>
          <Button variant="secondary" size="sm" className="bg-black text-white hover:bg-black/90 rounded-full px-4">
            Switch to Voice
          </Button>
        </div>

        {/* Main content */}
        <div className="flex flex-1 overflow-hidden">
          {/* Chat area */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}>
                  {message.sender === "user" ? (
                    <div className="flex items-start gap-3 max-w-[80%]">
                      <div className="bg-gray-100 rounded-lg p-3 order-1">
                        <p>{message.content}</p>
                      </div>
                      <Avatar className="w-8 h-8 order-2">
                        <AvatarImage src="/placeholder.svg?height=32&width=32" />
                        <AvatarFallback className="bg-gray-300">U</AvatarFallback>
                      </Avatar>
                    </div>
                  ) : (
                    <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
                      <p>{message.content}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Right sidebar */}
          <div className="w-80 border-l p-4 hidden md:block overflow-y-auto">
            <h2 className="font-bold text-lg mb-4">AI Tool Suggestions</h2>
            <div className="space-y-4">
              {[1, 2, 3].map((num) => (
                <Card key={num} className="p-4 shadow-sm">
                  <h3 className="font-bold">Tool Name {num}</h3>
                  <p className="text-sm text-gray-600">
                    A brief description of Tool Name {num} that highlights its key features and benefits.
                  </p>
                </Card>
              ))}
            </div>
          </div>
        </div>

        {/* Message input */}
        <div className="p-4 border-t">
          <div className="flex items-center gap-2">
            <Input
              placeholder="Type a message..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              className="rounded-full"
            />
            <div className="flex gap-1">
              <Button size="icon" variant="ghost" className="rounded-full bg-gray-100 hover:bg-gray-200">
                <Send className="h-5 w-5" />
              </Button>
              <Button size="icon" variant="ghost" className="rounded-full bg-gray-100 hover:bg-gray-200">
                <Paperclip className="h-5 w-5" />
              </Button>
              <Button size="icon" variant="ghost" className="rounded-full bg-gray-100 hover:bg-gray-200">
                <Mic className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

