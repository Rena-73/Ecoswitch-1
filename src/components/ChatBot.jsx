import { useState, useEffect, useRef } from 'react';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hi there! 👋 Welcome to EcoSwitch. I'm here to help you find eco-friendly alternatives. What would you like to know?",
      sender: 'bot',
      timestamp: new Date(),
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const botResponses = {
    // Greetings
    hello: "Hello! How can I help you find eco-friendly products today?",
    hi: "Hi! 👋 Welcome to EcoSwitch. I'm here to help!",
    hey: "Hey there! What eco-friendly products are you looking for?",
    
    // Product recommendations
    "recommend": "I can help you find eco-friendly products! What type of products are you interested in? We have:\n• Organic skincare\n• Sustainable fashion\n• Eco-friendly home products\n• Reusable items\n• And much more!",
    "product": "We have a wide range of eco-friendly products! You can browse our product section to find items based on your preferences, location, and eco-score.",
    
    // EcoScore questions
    "ecoscore": "EcoScore is a rating system that measures how sustainable a product is. Higher scores mean more eco-friendly! Visit our EcoScore Demo page to learn more.",
    "what is ecoscore": "EcoScore measures the environmental impact of products on a scale. It helps you make informed sustainable choices! 🌱",
    
    // Delivery and shipping
    "delivery": "We offer local delivery options in your area for faster service. Check product availability in your city!",
    "shipping": "We partner with local delivery services to provide fast and eco-friendly shipping options.",
    "how much": "Prices vary by product. Browse our product section to see all options and pricing!",
    
    // Sustainability questions
    "sustainable": "Great question! Sustainable products are made with minimal environmental impact and are designed to last longer. They help reduce waste and protect our planet!",
    "eco-friendly": "Eco-friendly products are made from sustainable materials, have lower carbon footprints, and are better for the environment. Every purchase makes a difference! 🌍",
    
    // Account related
    "account": "You can create an account to get personalized recommendations, track your orders, and earn eco-rewards!",
    "login": "Click on the Login/Sign Up button in the navigation bar to create an account.",
    "rewards": "Join our Rewards program to earn points on every eco-friendly purchase and unlock exclusive benefits!",
    
    // General help
    "help": "I can help you with:\n• Product recommendations\n• EcoScore information\n• Account setup\n• Order information\n• Sustainability tips\nJust ask me anything!",
    "contact": "You can reach our support team through the Contact page or email us directly!",
    "support": "Our support team is here to help! Visit the Contact page for more information.",
  };

  const getResponse = (userMessage) => {
    const lowerMessage = userMessage.toLowerCase().trim();
    
    // Check for exact matches first
    if (botResponses[lowerMessage]) {
      return botResponses[lowerMessage];
    }
    
    // Check for partial matches
    for (const [key, response] of Object.entries(botResponses)) {
      if (lowerMessage.includes(key)) {
        return response;
      }
    }
    
    // Default response
    return "That's a great question! I'm still learning. You can visit our Products section to explore eco-friendly alternatives, or contact our support team for more detailed help. 🌿";
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;

    // Add user message
    const newUserMessage = {
      id: messages.length + 1,
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, newUserMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate bot typing delay
    setTimeout(() => {
      const botResponse = {
        id: messages.length + 2,
        text: getResponse(inputValue),
        sender: 'bot',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 500);
  };

  return (
    <div className="fixed bottom-6 right-6 z-40">
      {/* Chat Window */}
      {isOpen && (
        <div className="bg-white rounded-2xl shadow-2xl w-96 h-screen sm:h-96 flex flex-col mb-4 border border-green-200">
          {/* Header */}
          <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-4 rounded-t-2xl flex justify-between items-center">
            <div>
              <h3 className="font-bold text-lg">🌿 EcoChat</h3>
              <p className="text-xs text-green-100">Always here to help</p>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:bg-green-800 rounded-full p-1 transition-all"
            >
              ×
            </button>
          </div>

          {/* Messages Container */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-green-50 to-white">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-lg whitespace-pre-wrap ${
                    message.sender === 'user'
                      ? 'bg-green-600 text-white rounded-br-none'
                      : 'bg-gray-200 text-gray-800 rounded-bl-none'
                  }`}
                >
                  {message.text}
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg rounded-bl-none">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{animationDelay: '0.4s'}}></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <form onSubmit={handleSendMessage} className="border-t border-green-200 p-4 bg-white rounded-b-2xl">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Ask me anything..."
                className="flex-1 border border-green-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-600"
              />
              <button
                type="submit"
                className="bg-green-600 hover:bg-green-700 text-white rounded-lg px-4 py-2 transition-all font-semibold"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Chat Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-green-600 hover:bg-green-700 text-white rounded-full p-4 shadow-lg hover:shadow-xl transition-all transform hover:scale-110"
        title={isOpen ? 'Close chat' : 'Open chat'}
      >
        {isOpen ? '✕' : '💬'}
      </button>
    </div>
  );
};

export default ChatBot;
