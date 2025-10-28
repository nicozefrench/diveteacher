/**
 * MessageList Component
 * Scrollable list of chat messages
 */

import { useEffect, useRef } from 'react';
import { MessageItem } from './MessageItem';

export function MessageList({ messages }) {
  const bottomRef = useRef(null);
  
  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  if (messages.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center text-gray-500 p-8">
        <div className="text-center">
          <p className="text-lg mb-2">No messages yet</p>
          <p className="text-sm">Ask a question to get started</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="flex-1 overflow-y-auto p-6">
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}

