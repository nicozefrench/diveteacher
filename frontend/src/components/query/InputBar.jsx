/**
 * InputBar Component
 * Query input with send button
 */

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Send } from 'lucide-react';

export function InputBar({ onSend, disabled }) {
  const [input, setInput] = useState('');
  
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!input.trim() || disabled) return;
    
    onSend(input.trim());
    setInput('');
  };
  
  const handleKeyDown = (e) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };
  
  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4 bg-white">
      <div className="flex gap-3">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about diving..."
          disabled={disabled}
          rows={1}
          className="
            flex-1 resize-none rounded-lg border border-gray-300 px-4 py-3
            focus:outline-none focus:ring-2 focus:ring-dive-primary focus:border-transparent
            disabled:opacity-50 disabled:cursor-not-allowed
            max-h-32
          "
          style={{ 
            minHeight: '48px',
            height: 'auto'
          }}
          onInput={(e) => {
            e.target.style.height = 'auto';
            e.target.style.height = e.target.scrollHeight + 'px';
          }}
        />
        
        <Button 
          type="submit" 
          disabled={!input.trim() || disabled}
          className="self-end"
        >
          <Send size={20} />
          Send
        </Button>
      </div>
      
      <p className="text-xs text-gray-500 mt-2">
        Press Enter to send, Shift+Enter for new line
      </p>
    </form>
  );
}

