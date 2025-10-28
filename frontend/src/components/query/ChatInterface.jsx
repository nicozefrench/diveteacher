import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { Card, CardHeader, CardBody, CardTitle, CardDescription } from '../ui/Card';
import { Button } from '../ui/Button';
import MessageList from './MessageList';
import { streamQuery } from '../../lib/api';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isStreaming) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsStreaming(true);

    const assistantMessage = {
      id: Date.now() + 1,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      isStreaming: true,
      facts: [],
      stats: {},
    };

    setMessages(prev => [...prev, assistantMessage]);

    try {
      await streamQuery(
        input.trim(),
        (token) => {
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, content: msg.content + token }
                : msg
            )
          );
        },
        (stats) => {
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, isStreaming: false, stats }
                : msg
            )
          );
          setIsStreaming(false);
        },
        (error) => {
          setMessages(prev =>
            prev.map(msg =>
              msg.id === assistantMessage.id
                ? { ...msg, content: `Error: ${error}`, isStreaming: false, error: true }
                : msg
            )
          );
          setIsStreaming(false);
        }
      );
    } catch (err) {
      console.error('Stream error:', err);
      setIsStreaming(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col gap-6">
      {/* Info Banner */}
      <div className="rounded-lg border border-primary-200 bg-primary-50 p-4">
        <div className="flex items-start gap-3">
          <Sparkles className="h-5 w-5 flex-shrink-0 text-primary-600" />
          <div>
            <h4 className="text-sm font-medium text-primary-900">
              RAG-Powered AI Assistant
            </h4>
            <p className="mt-1 text-sm text-primary-700">
              Ask questions about diving, decompression, Nitrox, equipment, and more.
              Responses are generated from uploaded documents in the knowledge graph.
            </p>
          </div>
        </div>
      </div>

      {/* Chat Card */}
      <Card className="flex flex-col h-[600px]">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Chat with Knowledge Graph</CardTitle>
              <CardDescription>
                {messages.length > 0 
                  ? `${Math.floor(messages.length / 2)} messages exchanged`
                  : 'Start a conversation by asking a question'}
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        {/* Messages */}
        <CardBody className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-gray-100">
                <svg
                  className="h-6 w-6 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                  />
                </svg>
              </div>
              <h3 className="mt-4 text-sm font-semibold text-gray-900">No messages yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Ask a question to get started
              </p>
            </div>
          ) : (
            <>
              <MessageList messages={messages} />
              <div ref={messagesEndRef} />
            </>
          )}
        </CardBody>

        {/* Input */}
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="flex gap-2">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about diving..."
              rows={2}
              disabled={isStreaming}
              className="flex-1 resize-none rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isStreaming}
              className="self-end"
            >
              <Send className="h-4 w-4" />
              {isStreaming ? 'Sending...' : 'Send'}
            </Button>
          </div>
          <p className="mt-2 text-xs text-gray-500">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </Card>
    </div>
  );
};

export default ChatInterface;
