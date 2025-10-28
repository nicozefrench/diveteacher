/**
 * ChatInterface Component
 * Main chat UI with SSE streaming
 */

import { useState, useCallback } from 'react';
import { MessageList } from './MessageList';
import { InputBar } from './InputBar';
import { ContextDisplay } from './ContextDisplay';
import { streamQuery } from '@/lib/api';
import { AlertCircle } from 'lucide-react';

export function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [currentContext, setCurrentContext] = useState(null);
  
  const handleSend = useCallback(async (question) => {
    if (!question.trim() || isStreaming) return;
    
    setError(null);
    setCurrentContext(null);
    
    // Add user message
    const userMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: question,
      timestamp: Date.now()
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    // Add empty assistant message (will be filled by streaming)
    const assistantId = `assistant-${Date.now()}`;
    const assistantMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      streaming: true,
      timestamp: Date.now(),
      context: null,
      stats: null
    };
    
    setMessages(prev => [...prev, assistantMessage]);
    setIsStreaming(true);
    
    try {
      // Stream response from backend
      for await (const event of streamQuery(question)) {
        if (event.token) {
          // Append token to assistant message
          setMessages(prev => prev.map(msg => 
            msg.id === assistantId 
              ? { ...msg, content: msg.content + event.token }
              : msg
          ));
        } else if (event.done) {
          // Finalize message with stats
          setMessages(prev => prev.map(msg => 
            msg.id === assistantId 
              ? { 
                  ...msg, 
                  streaming: false, 
                  stats: {
                    token_count: event.token_count,
                    duration_seconds: event.duration_seconds,
                    tokens_per_second: event.tokens_per_second,
                    context_facts: event.context_facts
                  }
                }
              : msg
          ));
          
          setIsStreaming(false);
        } else if (event.error) {
          // Handle streaming error
          throw new Error(event.error);
        } else if (event.context) {
          // Save context for display
          setCurrentContext(event.context);
          setMessages(prev => prev.map(msg => 
            msg.id === assistantId 
              ? { ...msg, context: event.context }
              : msg
          ));
        }
      }
    } catch (err) {
      console.error('Query error:', err);
      setError(err.message || 'Failed to get response. Please try again.');
      
      // Mark assistant message as failed
      setMessages(prev => prev.map(msg => 
        msg.id === assistantId 
          ? { 
              ...msg, 
              streaming: false, 
              content: msg.content || '❌ Failed to get response',
              error: true
            }
          : msg
      ));
      
      setIsStreaming(false);
    }
  }, [isStreaming]);
  
  return (
    <div className="dive-container py-6 h-full flex flex-col">
      <div className="flex-1 flex flex-col bg-white rounded-lg shadow-md overflow-hidden">
        {/* Context Display */}
        {currentContext && (
          <div className="p-4 border-b">
            <ContextDisplay facts={currentContext} />
          </div>
        )}
        
        {/* Error Display */}
        {error && (
          <div className="p-4 bg-red-50 border-b border-red-200 flex items-start gap-2">
            <AlertCircle className="text-red-500 flex-shrink-0 mt-0.5" size={20} />
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}
        
        {/* Message List */}
        <MessageList messages={messages} />
        
        {/* Input Bar */}
        <InputBar onSend={handleSend} disabled={isStreaming} />
      </div>
      
      {/* Helper text */}
      <p className="text-center text-sm text-gray-500 mt-4">
        Ask questions about diving, decompression, Nitrox, equipment, and more.
        <br />
        Responses are generated from uploaded documents in the knowledge graph.
      </p>
    </div>
  );
}

