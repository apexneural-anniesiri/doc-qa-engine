import { useState, useRef, useEffect } from "react";
import { sendMessage } from "../api";
import { MessageBubble } from "./MessageBubble";
import type { Source } from "../api";

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  sources?: Source[];
  timestamp: Date;
}

interface ChatProps {
  docId: string;
}

export function Chat({ docId }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: input.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await sendMessage(input.trim(), docId);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response.answer,
        isUser: false,
        sources: response.sources,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: `Error: ${error instanceof Error ? error.message : "Failed to get response"}`,
        isUser: false,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto w-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 mb-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-8">
            <p className="text-lg mb-2">Ask a question about your document</p>
            <p className="text-sm">I'll answer based on the content I've indexed.</p>
          </div>
        )}

        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message.text}
            isUser={message.isUser}
            sources={message.sources}
            timestamp={message.timestamp}
          />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
              <div className="flex items-center space-x-2">
                <div className="animate-pulse flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full delay-75"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full delay-150"></div>
                </div>
                <span className="text-gray-400 text-sm">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="border-t border-gray-700 p-4 bg-gray-900/50">
        <div className="flex space-x-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question... (Enter to send, Shift+Enter for newline)"
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={1}
            style={{
              minHeight: "48px",
              maxHeight: "120px",
            }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = "auto";
              target.style.height = `${Math.min(target.scrollHeight, 120)}px`;
            }}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed transition-colors font-medium"
          >
            Send
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send, Shift+Enter for newline
        </p>
      </div>
    </div>
  );
}
