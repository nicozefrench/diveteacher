import { User, Bot, Loader2, Clock } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { cn } from '../../lib/utils';

const MessageItem = ({ message }) => {
  const { role, content, isStreaming, stats, error, facts } = message;
  const isUser = role === 'user';

  return (
    <div className={cn("flex gap-3", isUser && "flex-row-reverse")}>
      {/* Avatar */}
      <div
        className={cn(
          "flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-primary-100" : "bg-gray-100"
        )}
      >
        {isUser ? (
          <User className="h-4 w-4 text-primary-700" />
        ) : (
          <Bot className="h-4 w-4 text-gray-600" />
        )}
      </div>

      {/* Content */}
      <div className={cn("flex-1 space-y-2", isUser && "flex flex-col items-end")}>
        {/* Message Bubble */}
        <div
          className={cn(
            "inline-block rounded-lg px-4 py-2.5 text-sm max-w-[80%]",
            isUser
              ? "bg-primary-500 text-white"
              : error
              ? "bg-error-50 text-error-900 border border-error-200"
              : "bg-white border border-gray-200 text-gray-900"
          )}
        >
          {isUser ? (
            <p className="whitespace-pre-wrap">{content}</p>
          ) : (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{content}</ReactMarkdown>
              {isStreaming && (
                <span className="inline-flex items-center gap-1 text-gray-400">
                  <Loader2 className="h-3 w-3 animate-spin" />
                  Thinking...
                </span>
              )}
            </div>
          )}
        </div>

        {/* Facts (if available) */}
        {!isUser && facts && facts.length > 0 && (
          <div className="rounded-lg bg-gray-50 p-3 text-xs">
            <p className="font-medium text-gray-700 mb-2">Retrieved Context:</p>
            <ul className="space-y-1 text-gray-600">
              {facts.slice(0, 3).map((fact, index) => (
                <li key={index} className="flex gap-2">
                  <span className="text-gray-400">•</span>
                  <span>{fact}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Stats */}
        {!isUser && stats && !isStreaming && (
          <div className="flex items-center gap-3 text-xs text-gray-500">
            <div className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              <span>{stats.duration_seconds?.toFixed(1)}s</span>
            </div>
            {stats.tokens_per_second && (
              <span>{stats.tokens_per_second.toFixed(1)} tok/s</span>
            )}
            {stats.token_count && (
              <span>{stats.token_count} tokens</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageItem;
