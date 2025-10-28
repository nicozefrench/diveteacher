/**
 * MessageItem Component
 * Individual chat message (user or assistant)
 * Supports markdown rendering and streaming
 */

import ReactMarkdown from 'react-markdown';
import { User, Bot, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

export function MessageItem({ message }) {
  const isUser = message.role === 'user';
  
  return (
    <div className={cn('message-item', isUser ? 'user' : 'assistant')}>
      {/* Avatar */}
      <div className="message-avatar">
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </div>
      
      {/* Content */}
      <div className="message-content">
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div>
            {message.content ? (
              <ReactMarkdown>{message.content}</ReactMarkdown>
            ) : (
              <span className="text-gray-400 italic">Waiting for response...</span>
            )}
            
            {message.streaming && (
              <Loader2 className="inline-block ml-2 animate-spin" size={16} />
            )}
          </div>
        )}
        
        {/* Context facts (if any) */}
        {!isUser && message.context && message.context.length > 0 && (
          <div className="message-context">
            <p className="text-sm text-gray-600 mb-2">
              📚 Retrieved {message.context.length} facts
            </p>
            <div className="space-y-1">
              {message.context.map((fact, idx) => (
                <div key={idx} className="dive-badge dive-badge-info text-xs">
                  {fact}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Stats (if done) */}
        {!isUser && message.stats && (
          <div className="message-stats">
            <span className="text-xs text-gray-500">
              {message.stats.token_count} tokens
              {message.stats.tokens_per_second && 
                ` · ${message.stats.tokens_per_second} tok/s`
              }
              {message.stats.duration_seconds && 
                ` · ${message.stats.duration_seconds}s`
              }
            </span>
          </div>
        )}
      </div>
    </div>
  );
}

