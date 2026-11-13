// ChatHistory.jsx
import React, { useState,useEffect, useRef, forwardRef, useImperativeHandle } from 'react';
import { MessageBox } from 'react-chat-elements';
import 'react-chat-elements/dist/main.css';

const ChatHistory = forwardRef((props, ref) => {
  const [messages, setMessages] = useState([]);
  const bottomRef = useRef(null); // For auto-scroll

  const addMessage = (text, sender = 'user', loading = false) => {
    setMessages((prev) => [
      ...prev,
      {
        position: sender === 'user' ? 'right' : 'left',
        text,
        title: sender === 'user' ? 'User' : 'Assistant',
        date: new Date(),
        loading,
      },
    ]);
  };
  const removeMessage = (index = null) => {
    setMessages((prev) => {
      if (index === null) return []; // remove all
      return prev.filter((_, i) => i !== index); // remove specific index
    });
  };
  const removeMessageLast = () => {
    setMessages((prev) => prev.slice(0, -1));
  };

 // Auto-scroll to bottom when messages update
 useEffect(() => {
  if (bottomRef.current) {
    bottomRef.current.scrollIntoView({ behavior: 'smooth' });
  }
}, [messages]);

  // Expose addMessage to parent
  useImperativeHandle(ref, () => ({
    addMessage,removeMessage,removeMessageLast
  }));

  return (
<div className="space-y-2">
    <MessageBox className="flex justify-start"
      position="left"
      type="text"
      text={
        <div className="text-justify">
          Hi there! I’m Hucenrotia Assistant, I can help you design or refine your automation project.
          <br />
          Let's turn ideas into reality!
        </div>}
      date={new Date()}
      title="Assistant"
    />

  {messages.map((msg, index) => (

      <MessageBox
        position={msg.position}
        type="text"
        text={ msg.loading ? (
          <div className="flex gap-1 text-gray-500 italic">
            <span className="animate-bounce delay-0">.</span>
            <span className="animate-bounce delay-100">.</span>
            <span className="animate-bounce delay-200">.</span>
          </div>
        ) : (
          <div className="text-justify">{msg.text}</div>
        )}
        title={msg.title}
        date={msg.date}
      />
  ))}
        <div ref={bottomRef} />

</div>
  );
});

export default ChatHistory;
