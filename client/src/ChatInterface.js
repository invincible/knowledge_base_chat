import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [buttons, setButtons] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // Инициализация чата при загрузке страницы
    initializeChat();
  }, []);

  const initializeChat = async () => {
    try {
      const response = await axios.post('/chat', { input: '' });
      setMessages([{ type: 'bot', text: response.data.response }]);
      setButtons(response.data.buttons);
    } catch (error) {
      console.error('Error initializing chat:', error);
    }
  };

  const sendMessage = async () => {
    if (input.trim() === '') return;

    try {
      const response = await axios.post('/chat', { input });
      setMessages([...messages, { type: 'user', text: input }, { type: 'bot', text: response.data.response }]);
      setButtons(response.data.buttons);
      setInput('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

return (
    <div className="chat-interface">
      <button onClick={() => navigate('/admin')}>Админка</button>
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type}`}>
            {msg.text}
          </div>
        ))}
      </div>
      <div className="buttons">
        {buttons.map((button, index) => (
          <button key={index} onClick={() => setInput(button)}>
            {button}
          </button>
        ))}
      </div>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
      />
      <button onClick={sendMessage}>Отправить</button>
    </div>
  );
};

export default ChatInterface;