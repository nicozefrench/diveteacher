import MessageItem from './MessageItem';

const MessageList = ({ messages }) => {
  return (
    <div className="space-y-6">
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
    </div>
  );
};

export default MessageList;
